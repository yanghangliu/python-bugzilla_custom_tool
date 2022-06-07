import bugzilla
import time


from settings import BUGZILLA_API_TOKEN
from settings import BUGZILLA_URL
from settings import TIME_FILTER
from settings import KVM_TEAM_MEMBER
from settings import TEAM_MEMBER_BUGZILLA_API_KEY_DICT
from settings import BUGZILLA_USER
from settings import OPEN_BUG_STATUS_LIST
from settings import VALID_BUG_RESOLUTION

QE_TEST_COVERAGE_FLAG_1 = "qe_test_coverage+"
QE_TEST_COVERAGE_FLAG_2 = "qe_test_coverage?"


def get_bugs_obj_with_status_and_flag(bzapi, username, flag, bug_status):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag, status=bug_status)
    query_dict["limit"] = 0
    bug_object_list = bzapi.query(query_dict)
    return bug_object_list


def save_bz_object_info(bug_object_list, log_path):
    bug_info_list = [(bug.qa_contact, str(bug.id), bug.summary, bug.weburl) for bug in bug_object_list]
    tmp_bug_list = ["   ".join(bug) for bug in bug_info_list]
    bug_str = "\n".join(tmp_bug_list)
    with open("%s", "w+" % log_path) as f:
        f.write(bug_str)


def get_bugs_obj_with_flag(bzapi, username, flag):
    query_dict = bzapi.build_query(qa_contact=username, flag=flag)
    query_dict["limit"] = 0
    bug_object_list = bzapi.query(query_dict)
    return bug_object_list


def filter_bugs_object(bzobj_list):
    bz_obj_list = []
    for bug in bzobj_list:
        if TIME_FILTER < bug.creation_time < "20220419T00:00:00":
            bz_obj_list.append(bug)
    return bz_obj_list


def main():
    bug_without_polarion_link_list = []
    bug_with_polarion_test_case_link_list = []
    bug_with_polarion_test_requirement_link_list = []
    bug_with_polarion_test_plan_link_list = []
    bug_with_wrong_polarion_link_list = []

    for leader in KVM_TEAM_MEMBER:
        group_member_list = KVM_TEAM_MEMBER[leader]

        bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=BUGZILLA_API_TOKEN)
        time.sleep(5)
        for member in group_member_list:
            # get all open bug with qe_test_coverage +

            bug_object_list_1 = []
            for bug_status in OPEN_BUG_STATUS_LIST:
                bug_object_1 = get_bugs_obj_with_status_and_flag(bzapi, member, QE_TEST_COVERAGE_FLAG_1, bug_status)
                bug_object_list_1 = bug_object_list_1 + bug_object_1

            bug_object_list_1 = filter_bugs_object(bug_object_list_1)
            print("%s open bug with qe_test_coverage+ number: %s" % (member, len(bug_object_list_1)))

            # get all valid bug with qe_test_coverage ?
            tmp_bug_object_list = get_bugs_obj_with_flag(bzapi, member, QE_TEST_COVERAGE_FLAG_2)
            bug_object_list_2 = []

            for bug_object in tmp_bug_object_list:
                if bug_object.resolution in VALID_BUG_RESOLUTION:
                    bug_object_list_2.append(bug_object)

            bug_object_list_2 = filter_bugs_object(bug_object_list_2)
            print("%s valid bug with qe_test_coverage? number: %s" % (member, len(bug_object_list_2)))

            bug_object_list = bug_object_list_1 + bug_object_list_2

            print("%s has %s bugs which need to check" % (member, len(bug_object_list)))

            if len(bug_object_list) > 0 and member != BUGZILLA_USER:
                if member in TEAM_MEMBER_BUGZILLA_API_KEY_DICT:
                    api_key = TEAM_MEMBER_BUGZILLA_API_KEY_DICT[member]
                    bzapi = bugzilla.Bugzilla(url=BUGZILLA_URL, api_key=api_key)
                    time.sleep(5)
                else:
                    print("please collect the bugzilla api key from %s" % member)
                    return None

            for bug_object in bug_object_list:
                bug_ext_info_list = bzapi.getbug(bug_object.id).external_bugs
                time.sleep(3)
                polarion_flag = 0
                for bug_ext_info_dict in bug_ext_info_list:

                    if bug_ext_info_dict['ext_bz_id'] in [117, 135, 116]:

                        polarion_flag = polarion_flag + 1
                        if bug_ext_info_dict['ext_bz_id'] == 117:
                            ext_bz_bug_id = bug_ext_info_dict['ext_bz_bug_id']

                            if ext_bz_bug_id.startswith("RHEL7-"):
                                new_ext_bz_bug_id = ext_bz_bug_id.replace("RHEL7", "VIRT")

                                bzapi.remove_external_tracker(bug_ids=bug_object.id, ext_type_id=117, ext_bz_bug_id=ext_bz_bug_id)

                                bzapi.add_external_tracker(bug_ids=bug_object.id, ext_bz_bug_id=new_ext_bz_bug_id, ext_type_id=117, ext_description="None")

                                check_list_1_1 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                bug_ext_info_dict['ext_bz_id'], ext_bz_bug_id, new_ext_bz_bug_id]

                                bug_with_polarion_test_case_link_list.append(check_list_1_1)

                            elif ext_bz_bug_id.startswith("RHEL-") or ext_bz_bug_id.startswith("VIRT-"):
                                new_ext_bz_bug_id = None

                                check_list_1_2 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                  bug_ext_info_dict['ext_bz_id'], ext_bz_bug_id, new_ext_bz_bug_id]
                                bug_with_polarion_test_case_link_list.append(check_list_1_2)
                            else:
                                new_ext_bz_bug_id = None
                                check_list_1_3 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                  bug_ext_info_dict['ext_bz_id'], ext_bz_bug_id, new_ext_bz_bug_id]
                                bug_with_wrong_polarion_link_list.append(check_list_1_3)

                        elif bug_ext_info_dict['ext_bz_id'] == 135:
                            ext_bz_bug_id = bug_ext_info_dict['ext_bz_bug_id']

                            if ext_bz_bug_id.startswith("RedHatEnterpriseLinux7"):
                                bzapi.remove_external_tracker(bug_ids=bug_object.id, ext_type_id=135, ext_bz_bug_id=ext_bz_bug_id)

                                replace_dict = {"RedHatEnterpriseLinux7": "RHELVIRT", "RHEL7-": "VIRT-"}
                                original_ext_bz_bug_id = ext_bz_bug_id
                                for k, n in replace_dict.items():
                                    ext_bz_bug_id = ext_bz_bug_id.replace(k, n)
                                new_ext_bz_bug_id = ext_bz_bug_id

                                bzapi.add_external_tracker(bug_ids=bug_object.id, ext_bz_bug_id=new_ext_bz_bug_id, ext_type_id=135, ext_description="None")
                                check_list_2_1 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                bug_ext_info_dict['ext_bz_id'], original_ext_bz_bug_id, new_ext_bz_bug_id]

                                bug_with_polarion_test_requirement_link_list.append(check_list_2_1)
                            else:
                                if not ext_bz_bug_id.startswith("RHELVIRT/"):
                                    original_ext_bz_bug_id = ext_bz_bug_id
                                    new_ext_bz_bug_id = None
                                    check_list_2_2 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                      bug_ext_info_dict['ext_bz_id'], original_ext_bz_bug_id,
                                                      new_ext_bz_bug_id]

                                    bug_with_wrong_polarion_link_list.append(check_list_2_2)

                        elif bug_ext_info_dict['ext_bz_id'] == 116:
                            ext_bz_bug_id = bug_ext_info_dict['ext_bz_bug_id']
                            if ext_bz_bug_id.startswith("RHEL7-"):
                                new_ext_bz_bug_id = ext_bz_bug_id.replace("RHEL7", "VIRT")

                                bzapi.remove_external_tracker(bug_ids=bug_object.id, ext_type_id=116, ext_bz_bug_id=ext_bz_bug_id)
                                bzapi.add_external_tracker(bug_ids=bug_object.id, ext_bz_bug_id=new_ext_bz_bug_id, ext_type_id=116, ext_description="None")
                                check_list_3_1 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                  bug_ext_info_dict['ext_bz_id'], ext_bz_bug_id, new_ext_bz_bug_id]

                                bug_with_polarion_test_plan_link_list.append(check_list_3_1)

                            elif ext_bz_bug_id.startswith("RHEL-") or ext_bz_bug_id.startswith("VIRT-"):
                                new_ext_bz_bug_id = None

                                check_list_3_2 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                  bug_ext_info_dict['ext_bz_id'], ext_bz_bug_id, new_ext_bz_bug_id]

                                bug_with_polarion_test_plan_link_list.append(check_list_3_2)
                            else:
                                new_ext_bz_bug_id = None
                                check_list_3_3 = [bug_object.id, bug_object.qa_contact, bug_object.weburl,
                                                  bug_ext_info_dict['ext_bz_id'], ext_bz_bug_id, new_ext_bz_bug_id]
                                bug_with_wrong_polarion_link_list.append(check_list_3_3)

                if polarion_flag == 0:
                    check_list_4 = [bug_object.id, bug_object.qa_contact, bug_object.weburl]
                    bug_without_polarion_link_list.append(check_list_4)

    print("The bugs without polarion link list is as following:")
    for n in bug_without_polarion_link_list:
        print(n)

    print("The bugs with polarion test case list is as following:")
    for n in bug_with_polarion_test_case_link_list:
        print(n)

    print("The bugs with polarion test requirement link list is as following:")
    for n in bug_with_polarion_test_requirement_link_list:
        print(n)

    print("The bugs with polarion test plan link list is as following:")
    for n in bug_with_polarion_test_plan_link_list:
        print(n)

    print("The bugs with wrong polarion link list is as following:")
    for n in bug_with_wrong_polarion_link_list:
        print(n)


main()
