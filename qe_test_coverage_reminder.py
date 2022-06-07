import bugzilla
import time

from gmail import send_gmail
from gmail import QE_TEST_COVERAGE_MAIL_CONTENT
from gmail import QE_TEST_COVERAGE_SUBJECT


from settings import BUGZILLA_API_TOKEN
from settings import BUGZILLA_URL
from settings import TIME_FILTER
from settings import KVM_AUTOTEST_PRODUCT
from settings import CVE_FLAG
from settings import INVALID_BUG_RESOLUTION
from settings import KVM_TEAM_MEMBER
from settings import RHEL_TEST_PRODUCT
from settings import PPC_FILTER_PLATFORM
from settings import KVM_VT_PRODUCT
from settings import MAIL_USERNAME


CORRECT_TEST_COVERAGE_FLAG = ["qe_test_coverage+", "qe_test_coverage-"]
REMINDER_BUG_STATUS_LIST = ["ON_QA", "VERIFIED", "CLOSED"]
WRONG_INVALID_BUG_FLAG = "qe_test_coverage+"
QA_ACK_MINUS_FLAG = "qa_ack-"


def login_bugzilla(bzapi, username, password):
    return bzapi.login(username, password)


def query_all_bugs(bzapi, username):
    query_all_bug = bzapi.build_query(qa_contact=username)
    query_all_bug["limit"] = 0
    all_bugs_object_list = bzapi.query(query_all_bug)
    return all_bugs_object_list


def query_set_flag_bugs(bzapi, username, flag):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag)
    query_dict["limit"] = 0
    set_flag_bug_object_list = bzapi.query(query_dict)
    return set_flag_bug_object_list


def filter_bugs(bugs_object_list):
    bugs_list = [(bug.qa_contact, str(bug.id), bug.status, bug.summary, bug.weburl)
                 for bug in bugs_object_list
                 if bug.creation_time > TIME_FILTER and
                 bug.status in REMINDER_BUG_STATUS_LIST and
                 bug.product != KVM_AUTOTEST_PRODUCT and
                 bug.product != RHEL_TEST_PRODUCT and
                 bug.platform not in PPC_FILTER_PLATFORM and
                 str(bug.id) != "1803680" and
                 str(bug.id) != "1832386" and
                 str(bug.id) != "1818764" and
                 str(bug.id) != "1856992" and
                 str(bug.id) != "1856993" and
                 str(bug.id) != "1828817" and
                 str(bug.id) != "1748741" and
                 str(bug.id) != "1869113" and
                 str(bug.id) != "1869020" and
                 str(bug.id) != "1905084" and
                 str(bug.id) != "1898018" and
                 str(bug.id) != "1874780" and
                 str(bug.id) != "1867739" and
                 str(bug.id) != "1904128" and
                 str(bug.id) != "1901896" and
                 str(bug.id) != "1814189" and
                 str(bug.id) != "1904268" and
                 str(bug.id) != "1819286" and
                 str(bug.id) != "1819274" and
                 str(bug.id) != "1840923" and
                 str(bug.id) != "1819284" and
                 str(bug.id) != "1894828" and
                 str(bug.id) != "1934158" and
                 str(bug.id) != "1934191" and
                 bug.product != KVM_VT_PRODUCT and
                 not set(CVE_FLAG) & set(bug.keywords)]
    return bugs_list


def query_set_flag_and_status_bugs(bzapi, username, state, flag):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag, status=state)
    query_dict["limit"] = 0
    set_flag_and_status_object_list = bzapi.query(query_dict)
    return set_flag_and_status_object_list


def filter_invalid_bug(bug_object_list):
    reminder_bugs_lists = [(bug.qa_contact, str(bug.id), bug.status, bug.summary, bug.weburl)
                           for bug in bug_object_list
                           if bug.creation_time > TIME_FILTER and
                           bug.resolution in INVALID_BUG_RESOLUTION and
                           bug.product != KVM_AUTOTEST_PRODUCT and
                           bug.platform not in PPC_FILTER_PLATFORM and
                           bug.product != KVM_VT_PRODUCT and
                           not set(CVE_FLAG) & set(bug.keywords)]
    return reminder_bugs_lists

# def filter_bugs(bugs_object_list):
#     bugs_list = []
#     for bug in bugs_object_list:
#         if bug.product != KVM_AUTOTEST_PRODUCT and not set(CVE_FLAG) & set(bug.keywords):
#             if bug.creation_time > TIME_FILTER and bug.status in REMINDER_BUG_STATUS_LIST:
#                 bugs_list.append((bug.qa_contact, str(bug.id), bug.status, bug.summary, bug.weburl))
#             if bug.creation_time < TIME_FILTER and bug.status in REMINDER_BUG_FILTER_STATUS_LIST:
#                 bugs_list.append((bug.qa_contact, str(bug.id), bug.status, bug.summary, bug.weburl))
#     return bugs_list


def main():
    bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=BUGZILLA_API_TOKEN)

    for leader in KVM_TEAM_MEMBER:
        reminder_bugs_list = []
        reminder_qa_list = []
        qa_bugs_dict = {}
        group_member_list = KVM_TEAM_MEMBER[leader]
        for mem in group_member_list:
            all_bugs_object_list = query_all_bugs(bzapi,mem)
            time.sleep(10)
            all_bugs_list = filter_bugs(all_bugs_object_list)
            set_correct_flag_bug_list = []
            for flag in CORRECT_TEST_COVERAGE_FLAG:
                set_correct_flag_bug_object_list = query_set_flag_bugs(bzapi, mem, flag)
                set_correct_flag_bug_list.extend(filter_bugs(set_correct_flag_bug_object_list))
            reminder_mem_bugs_list = list(set(all_bugs_list) - set(set_correct_flag_bug_list))
            
            invalid_bug_object_list = query_set_flag_and_status_bugs(bzapi, mem, "CLOSED", WRONG_INVALID_BUG_FLAG)
            reminder_invalid_bug_list = filter_invalid_bug(invalid_bug_object_list)

            reminder_mem_bugs_list.extend(reminder_invalid_bug_list)

            qa_ack_minus_object_list = query_set_flag_bugs(bzapi, mem, QA_ACK_MINUS_FLAG)
            qa_ack_minus_list = [(bug.qa_contact, str(bug.id), bug.status, bug.summary, bug.weburl)
                                 for bug in qa_ack_minus_object_list]

            for bug in qa_ack_minus_list:
                if bug in reminder_mem_bugs_list:
                    reminder_mem_bugs_list.remove(bug)

            # add all reminder bug of this member into the reminder_bugs_list
            reminder_bugs_list.extend(reminder_mem_bugs_list)

            if len(reminder_mem_bugs_list) > 0:
                reminder_qa_list.append(mem)
                qa_bugs_dict[mem] = len(reminder_mem_bugs_list)

        if len(reminder_bugs_list)> 0:
            reminder_bug = ["   ".join(bug) for bug in reminder_bugs_list]
            reminder_bug_info = "\n".join(reminder_bug)
            reminder_qa_bugs_info = ""
            for k, v in qa_bugs_dict.items():
                reminder_qa_bugs_info = reminder_qa_bugs_info + str(k) + " " + str(v) + "\n"
            mail_content = QE_TEST_COVERAGE_MAIL_CONTENT.format(qa_bugs=reminder_qa_bugs_info, bug_info=reminder_bug_info)
           
            cc_list = list(leader)
            cc_list.append(MAIL_USERNAME)
            send_gmail(MAIL_USERNAME, reminder_qa_list, cc_list, QE_TEST_COVERAGE_SUBJECT, mail_content)


if __name__ == "__main__":
    main()
