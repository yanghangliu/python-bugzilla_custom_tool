import bugzilla

from gmail import send_gmail
from gmail import QA_ACK_MAIL_CONTENT
from gmail import QA_ACK_SUBJECT


from settings import BUGZILLA_API_TOKEN
from settings import BUGZILLA_URL
from settings import KVM_AUTOTEST_PRODUCT
from settings import KVM_TEAM_MEMBER
from settings import RHEL_TEST_PRODUCT
from settings import KVM_VT_PRODUCT
from settings import MAIL_USERNAME

ALL_QA_ACK_FLAG = "qa_ack"
CORRECT_QA_ACK_FLAG = ["qa_ack+"]
REMINDER_BUG_STATUS_LIST = ["POST"]


def login_bugzilla(bzapi, username, password):
    return bzapi.login(username, password)


def query_set_flag_bugs(bzapi, username, flag):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag)
    query_dict["limit"] = 0
    bug_object_list = bzapi.query(query_dict)
    return bug_object_list


def filter_bugs(bugs_object_list):
    bugs_list = [(bug.qa_contact, str(bug.id), bug.status, bug.summary, bug.weburl)
                 for bug in bugs_object_list
                 if bug.status in REMINDER_BUG_STATUS_LIST and
                 bug.product != KVM_AUTOTEST_PRODUCT and
                 bug.product != RHEL_TEST_PRODUCT and
                 bug.product != KVM_VT_PRODUCT]
    return bugs_list


def main():
    bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=BUGZILLA_API_TOKEN)

    for leader in KVM_TEAM_MEMBER:
        reminder_bugs_list = []
        reminder_qa_list = []
        qa_bugs_dict = {}
        group_member_list = KVM_TEAM_MEMBER[leader]
        for mem in group_member_list:
            all_bugs_object_list = query_set_flag_bugs(bzapi, mem, ALL_QA_ACK_FLAG)
            all_bugs_list = filter_bugs(all_bugs_object_list)
            set_correct_flag_bug_list = []
            for flag in CORRECT_QA_ACK_FLAG:
                set_correct_flag_bug_object_list = query_set_flag_bugs(bzapi, mem, flag)
                set_correct_flag_bug_list.extend(filter_bugs(set_correct_flag_bug_object_list))
            reminder_mem_bugs_list = list(set(all_bugs_list) - set(set_correct_flag_bug_list))
            reminder_bugs_list.extend(reminder_mem_bugs_list)
            if len(reminder_mem_bugs_list) > 0:
                reminder_qa_list.append(mem)
                qa_bugs_dict[mem] = len(reminder_mem_bugs_list)
            print(reminder_bugs_list)

        if len(reminder_bugs_list) > 0:
            reminder_bug = ["   ".join(bug) for bug in reminder_bugs_list]
            reminder_bug_info = "\n".join(reminder_bug)
            reminder_qa_bugs_info = ""
            for k, v in qa_bugs_dict.items():
                reminder_qa_bugs_info = reminder_qa_bugs_info + str(k) + " " + str(v) + "\n"
            mail_content = QA_ACK_MAIL_CONTENT.format(qa_bugs=reminder_qa_bugs_info, bug_info=reminder_bug_info)
            cc_list = list(leader)
            send_gmail(MAIL_USERNAME, reminder_qa_list, cc_list, QA_ACK_SUBJECT, mail_content)


if __name__ == "__main__":
    main()
