import bugzilla
import time

from datetime import datetime
from datetime import timedelta

from gmail import send_gmail
from gmail import EXCEPTION_BUG_REMINDER_MAIL_CONTENT
from gmail import EXCEPTION_BUG_REMINDER_SUBJECT

from settings import MAIL_USERNAME
from settings import BUGZILLA_URL
from settings import KVM_TEAM_MEMBER
from settings import BUGZILLA_API_TOKEN
from settings import ITM_DATE_DICT
from settings import ITM_FLAG
from settings import ITR_FLAG


REMINDER_BUG_STATUS_LIST = ["NEW", "ASSIGNED", "POST", "MODIFIED", "ON_QA"]
ITR_REMINDER_LIST = ["8.7.0", "9.1.0"]
EXCEPTION_FLAG_1 = "exception+"
EXCEPTION_FLAG_2 = "exception?"
BLOCKER_FLAG_1 = "blocker+"
BLOCKER_FLAG_2 = "blocker?"
REMINDER_TEAM_FILTER_LIST = ["chayang@redhat.com", "coli@redhat.com", "lijin@redhat.com"]


def get_this_monday():
    today = time.strftime("%Y-%m-%d", time.localtime())
    today = datetime.strptime(str(today), "%Y-%m-%d")
    monday_date = datetime.strftime(today - timedelta(today.weekday()), "%Y-%m-%d")
    return monday_date


def query_set_flag_bugs(bzapi, username, flag):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag)
    query_dict["limit"] = 0
    bug_object_list = bzapi.query(query_dict)
    return bug_object_list


def filter_bugs(bugs_object_list):
    bugs_list = []
    for bug in bugs_object_list:
        if ITR_FLAG in dir(bug):
            itr = bug.cf_internal_target_release
        else:
            print("The bug whose id is %s does not have the %s" % (str(bug.id), ITR_FLAG))
            itr = "None"
        if bug.status in REMINDER_BUG_STATUS_LIST and itr in ITR_REMINDER_LIST:
            if ITM_FLAG in dir(bug):
                bugs_list.append((bug.qa_contact, "ITR:%s" % itr, "ITM:%s" % bug.cf_internal_target_milestone,
                                  bug.status, bug.summary, bug.weburl))
            else:
                bugs_list.append((bug.qa_contact, "ITR:%s" % itr, "ITM:null", bug.status, bug.summary, bug.weburl))
    return bugs_list


def main():
    date = get_this_monday()
    current_itm = ITM_DATE_DICT[date]
    if current_itm >= 27:
        bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=BUGZILLA_API_TOKEN)

        all_reminder_bugs_list_1 = []
        all_reminder_bugs_list_2 = []
        all_reminder_bugs_list_3 = []
        all_reminder_bugs_list_4 = []
        reminder_qa_list = []

        qa_bugs_dict = {}
        group_member_list = []

        for leader in KVM_TEAM_MEMBER:
            if leader[0] in REMINDER_TEAM_FILTER_LIST:
                group_member_list.extend(KVM_TEAM_MEMBER[leader])

        for mem in group_member_list:
            # get all the bugs with exception+ flag
            exception_bugs_object_list_1 = query_set_flag_bugs(bzapi, mem, EXCEPTION_FLAG_1)
            exception_bugs_reminder_list_1 = filter_bugs(exception_bugs_object_list_1)
            all_reminder_bugs_list_1.extend(exception_bugs_reminder_list_1)
            # get all the bugs with exception? flag
            exception_bugs_object_list_2 = query_set_flag_bugs(bzapi, mem, EXCEPTION_FLAG_2)
            exception_bugs_reminder_list_2 = filter_bugs(exception_bugs_object_list_2)
            all_reminder_bugs_list_2.extend(exception_bugs_reminder_list_2)
            # get all the bugs with block+ flag
            blocker_bugs_object_list_1 = query_set_flag_bugs(bzapi, mem, BLOCKER_FLAG_1)
            blocker_bugs_reminder_list_1 = filter_bugs(blocker_bugs_object_list_1)
            all_reminder_bugs_list_3.extend(blocker_bugs_reminder_list_1)
            #  get all the bugs with block? flag
            blocker_bugs_object_list_2 = query_set_flag_bugs(bzapi, mem, BLOCKER_FLAG_2)
            blocker_bugs_reminder_list_2 = filter_bugs(blocker_bugs_object_list_2)
            all_reminder_bugs_list_3.extend(blocker_bugs_reminder_list_2)

            if len(exception_bugs_reminder_list_1) > 0 or len(exception_bugs_reminder_list_2) > 0 \
                    or len(blocker_bugs_reminder_list_1) or len(blocker_bugs_reminder_list_2):
                reminder_qa_list.append(mem)
                reminder_mem_bugs_number = len(exception_bugs_reminder_list_1) + len(exception_bugs_reminder_list_2) + \
                                           len(blocker_bugs_reminder_list_1) + len(blocker_bugs_reminder_list_2)
                qa_bugs_dict[mem] = reminder_mem_bugs_number

        if len(reminder_qa_list) > 0:
            if len(all_reminder_bugs_list_1) > 0:
                reminder_bug_1 = ["   ".join(bug) for bug in all_reminder_bugs_list_1]
                reminder_bug_info_1 = "\n".join(reminder_bug_1)
            else:
                reminder_bug_info_1 = "NONE"

            if len(all_reminder_bugs_list_2) > 0:
                reminder_bug_2 = ["   ".join(bug) for bug in all_reminder_bugs_list_2]
                reminder_bug_info_2 = "\n".join(reminder_bug_2)
            else:
                reminder_bug_info_2 = "NONE"

            if len(all_reminder_bugs_list_3) > 0:
                reminder_bug_3 = ["   ".join(bug) for bug in all_reminder_bugs_list_3]
                reminder_bug_info_3 = "\n".join(reminder_bug_3)
            else:
                reminder_bug_info_3 = "NONE"

            if len(all_reminder_bugs_list_4) > 0:
                reminder_bug_4 = ["   ".join(bug) for bug in all_reminder_bugs_list_4]
                reminder_bug_info_4 = "\n".join(reminder_bug_4)
            else:
                reminder_bug_info_4 = "NONE"

            reminder_qa_bugs_info = ""
            for k, v in qa_bugs_dict.items():
                reminder_qa_bugs_info = reminder_qa_bugs_info + str(k) + " " + str(v) + "\n"
            mail_content = EXCEPTION_BUG_REMINDER_MAIL_CONTENT.format(qa_bugs=reminder_qa_bugs_info,
                                                                      bug_info_1=reminder_bug_info_1,
                                                                      bug_info_2=reminder_bug_info_2,
                                                                      bug_info_3=reminder_bug_info_3,
                                                                      bug_info_4=reminder_bug_info_4)

            # cc_list = KVM_TEMA_LEADER_LIST
            cc_list = REMINDER_TEAM_FILTER_LIST

            send_gmail(MAIL_USERNAME, reminder_qa_list, cc_list, EXCEPTION_BUG_REMINDER_SUBJECT, mail_content)
        print("current itm value is %s" % current_itm)


if __name__ == "__main__":
    main()
