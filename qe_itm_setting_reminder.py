import time
import bugzilla

from gmail import send_gmail
from gmail import ITM_SETTING_MAIL_CONTENT
from gmail import ITM_SETTING_SUBJECT

from settings import MAIL_USERNAME
from settings import CVE_FLAG
from settings import BUGZILLA_URL
from settings import KVM_TEAM_MEMBER
from settings import Z_STREAM_FLAG
from settings import KVM_TEMA_LEADER_LIST
from settings import BUGZILLA_API_TOKEN
from settings import ITM_FLAG
from settings import ITR_FLAG

QA_ACK_FLAG = "qa_ack+"
DEVEL_ACK_FLAG = "devel_ack+"


REMINDER_BUG_STATUS_LIST = ["NEW", "ASSIGNED", "POST", "MODIFIED", "ON_QA"]
ITR_REMINDER_LIST = ["8.7.0", "9.1.0"]


def login_bugzilla(bzapi, username, password):
    return bzapi.login(username, password)


def query_set_flag_bugs(bzapi, username, flag):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag)
    query_dict["limit"] = 0
    bug_object_list = bzapi.query(query_dict)
    time.sleep(5)
    return bug_object_list


def filter_bugs(bugs_object_list):
    bugs_list = []
    for bug in bugs_object_list:
        if ITR_FLAG in dir(bug):
            itr = bug.cf_internal_target_release
        else:
            print("The bug whose id is %s does not have the %s" % (str(bug.id), ITR_FLAG))
            itr = "None"
        if bug.status in REMINDER_BUG_STATUS_LIST and \
           itr in ITR_REMINDER_LIST and \
                not set(CVE_FLAG) & set(bug.keywords) and \
                not set(Z_STREAM_FLAG) & set(bug.keywords):
            if ITM_FLAG in dir(bug):
                # This bug whose ITM attribute is equals to ---"
                if bug.cf_internal_target_milestone == "---":
                    bugs_list.append((bug.qa_contact, "ITR:%s" % itr, bug.status, bug.summary, bug.weburl))
            else:
                # This bug do not have the ITM attribute"
                bugs_list.append((bug.qa_contact, "ITR:%s" % itr, bug.status, bug.summary, bug.weburl))
    return bugs_list


def main():
    bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=BUGZILLA_API_TOKEN)

    all_reminder_bugs_list = []
    reminder_qa_list = []
    qa_bugs_dict = {}
    group_member_list = []

    for leader in KVM_TEAM_MEMBER:
        group_member_list.extend(KVM_TEAM_MEMBER[leader])

    for mem in group_member_list:
        all_qa_ack_object_list = query_set_flag_bugs(bzapi, mem, QA_ACK_FLAG)
        qa_ack_reminder_list = filter_bugs(all_qa_ack_object_list)
        all_devel_ack_object_list = query_set_flag_bugs(bzapi, mem, DEVEL_ACK_FLAG)
        devel_ack_reminder_list = filter_bugs(all_devel_ack_object_list)
        reminder_mem_bugs_list = list(set(devel_ack_reminder_list) & set(qa_ack_reminder_list))

        all_reminder_bugs_list.extend(reminder_mem_bugs_list)
        if len(reminder_mem_bugs_list) > 0:
            reminder_qa_list.append(mem)
            qa_bugs_dict[mem] = len(reminder_mem_bugs_list)

    if len(all_reminder_bugs_list) > 0:
        reminder_bug = ["   ".join(bug) for bug in all_reminder_bugs_list]
        reminder_bug_info = "\n".join(reminder_bug)
        reminder_qa_bugs_info = ""
        for k, v in qa_bugs_dict.items():
            reminder_qa_bugs_info = reminder_qa_bugs_info + str(k) + " " + str(v) + "\n"

        cc_list = KVM_TEMA_LEADER_LIST
        cc_list.append(MAIL_USERNAME)
        mail_content = ITM_SETTING_MAIL_CONTENT.format(qa_bugs=reminder_qa_bugs_info, bug_info=reminder_bug_info)

        send_gmail(MAIL_USERNAME, reminder_qa_list, cc_list, ITM_SETTING_SUBJECT, mail_content)


if __name__ == "__main__":
    main()
