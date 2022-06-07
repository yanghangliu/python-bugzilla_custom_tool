QE bugzilla management tools

A toolkit to check for bug info and send out reminder emails automatically.

Directory role description:

├── gmail.py    

define email content and send reminder mail via GMAIL

├── qa_ack_reminder.py    

check for POST bugs without qa_ack+ flag 

├── qe_test_coverage_reminder.py    

check for bugs that are in ON_QA,VERIFIED,CLOSED status,but without qe_test_coverage+ nor qe_test_coverage-

├── qe_exception_reminder.py

check for exception bugs

├── qe_itm_setting.py

check for the bugs with qa_ack+ and devel+ but without itm settings

├── qe_itm_expire_reminder.py

check for the bugs whose ITM will be expiring

├── settings.py   

save some basic information and only run this tool after editing this file


How to use this toolkit?

1.Download and install appropriat python-bugzilla package

`# pip3 install python-bugzilla`

2.Choose a gmail account for sending reminder mails
 
(1)start pop3/smtp/imap service

(2)setup an app password

3.edit settings.py

(1)input the gmail username and app password in MAIL_USERNAME and MAIL_PASSWORD respectively.

The MAIL_USERNAME and MAILPASSWORD will be used to login to gmail server.

(3)input the email addresses of team members and managers in GROUP_MEMBER_LIST and MANAGER_LIST respectively.

This tool will check for the bug info of the team members in turn.

For bugs that are not properly formatted, this tool will automatically send reminder emails and cc manager.

(4)input the bugzilla username and bugzilla api key in BUGAZILLA_USER and BUGZILLA_API_TOKEN respectively.

The BUGAZILLA_USER and BUGZILLA_API_TOKEN will be used to login to bugzilla account.

(5)Just run the different *.py script with the help of crond service

such as:

crontab -e

00 06 * * * /usr/bin/python3 /home/qe-management-tools/qe_test_coverage_reminder.py

30 06 * * * /usr/bin/python3 /home/qe-management-tools/qa_ack_reminder.py
