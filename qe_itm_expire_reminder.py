import time
import bugzilla

from datetime import datetime
from datetime import timedelta

from gmail import send_gmail
from gmail import EXPIRING_ITM_MAIL_CONTENT
from gmail import EXPIRING_ITM_SUBJECT

from settings import MAIL_USERNAME
from settings import BUGZILLA_URL
from settings import KVM_TEAM_MEMBER
from settings import KVM_TEMA_LEADER_LIST
from settings import BUGZILLA_API_TOKEN
from settings import ITM_DATE_DICT
from settings import ITM_FLAG
from settings import ITR_FLAG

REMINDER_BUG_STATUS_LIST = ["NEW", "ASSIGNED", "POST", "MODIFIED", "ON_QA"]
ITR_REMINDER_LIST = ["8.7.0", "9.1.0"]


def get_today_date():
    return datetime.today().strftime('%Y-%m-%d')


def get_this_monday():
    today = time.strftime("%Y-%m-%d", time.localtime())
    today = datetime.strptime(str(today), "%Y-%m-%d")
    monday_date = datetime.strftime(today - timedelta(today.weekday()), "%Y-%m-%d")
    return monday_date


def get_itm(date, itm_dict):
    if date in itm_dict.keys():
        return itm_dict[date]


def query_all_bugs_object(bzapi, username):
    query_all_bug = bzapi.build_query(qa_contact=username)
    query_all_bug["limit"] = 0
    all_bugs_object_list = bzapi.query(query_all_bug)
    return all_bugs_object_list


def main():
    bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=BUGZILLA_API_TOKEN)

    all_reminder_bugs_list = []
    reminder_qa_list = []
    qa_bugs_dict = {}

    group_member_list = []
    # for leader in KVM_TEAM_MEMBER:
    #     group_member_list.extend(KVM_TEAM_MEMBER[leader])
    leader = ("chayang@redhat.com",)
    group_member_list.extend(KVM_TEAM_MEMBER[leader])

    date = get_this_monday()
    itm = get_itm(date, ITM_DATE_DICT)

    for mem in group_member_list:
        all_object_list = query_all_bugs_object(bzapi, mem)
        expiring_itm_bugs_list = []
        for bug in all_object_list:
            if ITR_FLAG in dir(bug):
                itr = bug.cf_internal_target_release
            else:
                print("The bug whose id is %s does not have the %s" % (str(bug.id), ITR_FLAG))
                itr = "None"
            if bug.status in REMINDER_BUG_STATUS_LIST and itr in ITR_REMINDER_LIST and ITM_FLAG in dir(bug) and bug.cf_internal_target_milestone != "---":
                if int(bug.cf_internal_target_milestone) <= itm + 1:
                    expiring_itm_bugs_list.append((bug.qa_contact, "ITR:%s" % itr, "ITM:%s" % bug.cf_internal_target_milestone,
                                                   bug.status, bug.summary, bug.weburl))

        all_reminder_bugs_list.extend(expiring_itm_bugs_list)
        if len(expiring_itm_bugs_list) > 0:
            reminder_qa_list.append(mem)
            qa_bugs_dict[mem] = len(expiring_itm_bugs_list)

    if len(all_reminder_bugs_list) > 0:
        reminder_bug = ["   ".join(bug) for bug in all_reminder_bugs_list]
        reminder_bug_info = "\n".join(reminder_bug)
        reminder_qa_bugs_info = ""
        for k, v in qa_bugs_dict.items():
            reminder_qa_bugs_info = reminder_qa_bugs_info + str(k) + " " + str(v) + "\n"

        # cc_list = KVM_TEMA_LEADER_LIST
        # cc_list.append(MAIL_USERNAME)

        cc_list = ["chayang@redhat.com", "yanghliu@redhat.com"]

        mail_content = EXPIRING_ITM_MAIL_CONTENT.format(itm=itm, qa_bugs=reminder_qa_bugs_info, bug_info=reminder_bug_info)

        send_gmail(MAIL_USERNAME, reminder_qa_list, cc_list, EXPIRING_ITM_SUBJECT, mail_content)


if __name__ == "__main__":
    main()




