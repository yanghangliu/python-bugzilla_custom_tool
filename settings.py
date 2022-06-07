"""
Project settings for qe_management toolkit
"""

# check for the bug info of the group members list in turn.
# For bugs that are not properly formatted, this tool will automatically send reminder emails and cc manager.

CHAYANG_TEAM_MEMBER_LIST = ["yanghliu@redhat.com", "leiyang@redhat.com", "pezhang@redhat.com", "chayang@redhat.com",
                            "yuhuang@redhat.com", "nanliu@redhat.com", "xiaohli@redhat.com", "wquan@redhat.com",
                            "yama@redhat.com", "mcasquer@redhat.com"]

COLI_TEAM_MEMBER_LIST = ["qinwang@redhat.com", "qcheng@redhat.com", "aliang@redhat.com", "yduan@redhat.com",
                         "xuwei@redhat.com", "zhguo@redhat.com", "coli@redhat.com", "zixchen@redhat.com",
                         "timao@redhat.com", "jinl@redhat.com"]

LIJIN_TEAM_MEMBER_LIST = ["lijin@redhat.com", "mdeng@redhat.com", "xuma@redhat.com", "zhenyzha@redhat.com",
                          "ngu@redhat.com", "yihyu@redhat.com", "bfu@redhat.com", "bmarcynk@redhat.com"]

QIZHU_TEAM_MEMBER_LIST = ["qizhu@redhat.com", "phou@redhat.com", "xiagao@redhat.com",
                          "menli@redhat.com", "demeng@redhat.com", "leidwang@redhat.com",
                          "mama@redhat.com"]

JUZHANG_TEAM_MEMBER_LIST = ["juzhang@redhat.com", "xuhan@redhat.com", "xfu@redhat.com", "zhencliu@redhat.com",
                            "yfu@redhat.com", "yhong@redhat.com", "lkotek@redhat.com", "chdong@redhat.com",
                            "bgartzia@redhat.com", "hzuo@redhat.com"]

JINZHAO_TEAM_MEMBER_LIST = ["jinzhao@redhat.com", "yiwei@redhat.com"]

KVM_TEAM_MEMBER = {
    ("chayang@redhat.com",): CHAYANG_TEAM_MEMBER_LIST,
    ("coli@redhat.com",): COLI_TEAM_MEMBER_LIST,
    ("jinzhao@redhat.com",): JINZHAO_TEAM_MEMBER_LIST,
    ("lijin@redhat.com",): LIJIN_TEAM_MEMBER_LIST,
    ("juzhang@redhat.com",): JUZHANG_TEAM_MEMBER_LIST,
    ("qizhu@redhat.com", "juzhang@redhat.com"): QIZHU_TEAM_MEMBER_LIST,
}

KVM_TEMA_LEADER_LIST = ["chayang@redhat.com", "coli@redhat.com", "jinzhao@redhat.com", "lijin@redhat.com",
                        "juzhang@redhat.com", "qizhu@redhat.com"]



# login to bugzilla
BUGZILLA_USER = "REPLACE_WITH_BUGZILLA_USERNAME"
BUGZILLA_URL = "bugzilla.redhat.com"
BUGZILLA_API_TOKEN = "REPLACE_WITH_API_KEY"

# login to gmail
MAIL_USERNAME = "REPLACE_GMAIL_USERNAME"
MAIL_PASSWORD = "REPLACE_GMAIL_PASSWORD"


# some filter
Z_STREAM_FLAG = ["ZStream", "ZStreamTracked"]
CVE_FLAG = ["Security", "SecurityTracking", "Tracking"]
KVM_AUTOTEST_PRODUCT = "KVM_Autotest"
TIME_FILTER = "20190901T00:00:00"
PPC_FILTER_PLATFORM = ["s390x", "aarch64"]
RHEL_TEST_PRODUCT = "RHEL Tests"
KVM_VT_PRODUCT = "Virtualization Tools"
INVALID_BUG_RESOLUTION = ["NOTABUG", "WONTFIX", "DUPLICATE", "CANTFIX", "INSUFFICIENT_DATA", "WORKSFORME", "RAWHIDE",
                          "NEXTRELEASE", "UPSTREAM", "EOL", "DEFERRED"]
OPEN_BUG_STATUS_LIST = ["NEW", "ASSIGNED", "POST", "MODIFIED", "ON_QA", "VERIFIED", "ON_DEV", "RELEASE_PENDING"]

VALID_BUG_RESOLUTION = ["ERRATA", "CURRENTRELEASE", ""]
ITM_FLAG = "cf_internal_target_milestone"
ITR_FLAG = "cf_internal_target_release"
CLOSED_BUG_STATUS_STR = "CLOSED"



# TEMA_MEMBER_BUGZILLA_API DOC : related link: https://docs.google.com/spreadsheets/d/1rDy3-IJQN0hFUYIY14jFCpXFQpIzLcRAEzXJZePA06M/edit#gid=1010792859
TEAM_MEMBER_BUGZILLA_API_KEY_DICT = {'USER1': 'KEY1',
                                     'USER2': 'KEY2'
                                     }


ITM_DATE_DICT = {
    "2022-03-07": 1,
    "2022-03-14": 2,
    "2022-03-21": 3,
    "2022-03-28": 4,
    "2022-04-04": 5,
    "2022-04-11": 6,
    "2022-04-18": 7,
    "2022-04-25": 8,
    "2022-05-02": 9,
    "2022-05-09": 10,
    "2022-05-16": 11,
    "2022-05-23": 12,
    "2022-05-30": 13,
    "2022-06-06": 14,
    "2022-06-13": 15,
    "2022-06-20": 16,
    "2022-06-27": 17,
    "2022-07-04": 18,
    "2022-07-11": 19,
    "2022-07-18": 20,
    "2022-07-25": 21,
    "2022-08-01": 22,
    "2022-08-08": 23,
    "2022-08-15": 24,
    "2022-08-22": 25,
    "2022-08-29": 26,
    "2022-09-05": 27,
    "2022-09-12": 28,
    "2022-09-19": 29,
    "2022-09-26": 30,
    "2022-10-03": 31,
    "2022-10-10": 32,
    "2022-10-17": 33,
    "2022-10-24": 34,
    "2022-10-31": 35,
    "2022-11-07": 36,
}