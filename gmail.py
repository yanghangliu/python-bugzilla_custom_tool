import smtplib
import time
import os
from email.header import Header
from email.mime.text import MIMEText


QE_TEST_COVERAGE_MAIL_CONTENT="""
Hi all, 
You receive this mail because we have bugs that are in ON_QA,VERIFIED,CLOSED status, but without correct qe_test_coverage+ or qe_test_coverage-. 
(our tool will send this reminder email on the last Wednesday of every month)
Please review the following bugs as soon as possible and set the right qe_test_coverage flag.

please feel free to let me know which bugs are manual-only, so that I can blacklist them.


The QA contact and bug number are as following: 
{qa_bugs}

The detailed bug info list is as following:
{bug_info}

"""

QA_ACK_MAIL_CONTENT = """
Hi all, 
You receive this mail because we have bugs that are in POST status, but without qa_ack+. 
Please review the following bugs as soon as possible and set the right qa_ack+ flag. 
If you find any issues or have any suggestions/questions about this tool, please feel free to contact yanghliu@redhat.com.


The qa_contact and bug number are as following: 
{qa_bugs}

The detailed bug info list is as following:
{bug_info}
"""


ITM_SETTING_MAIL_CONTENT = """
Hi all,
You receive this mail because we have bugs that have qa_ack+ and devel_ack+, but without ITM settings.
(our tool will send this reminder email every Monday morning)
Please review the following bugs as soon as possible and set the right ITM flag.
If you find any issues or have any suggestions/questions about this tool, please feel free to contact yanghliu@redhat.com.


The qa_contact and bug number are as following:
{qa_bugs}

The detailed bug info list is as following:
{bug_info}
"""

EXPIRING_ITM_MAIL_CONTENT = """
Hi all,
Today is ITM-{itm}.
You receive this mail because we have open bugs whose ITM has been expiring or will be expiring soon.
Please review the following bugs as soon as possible and reset ITM flag.
If you find any issues or have any suggestions/questions about this tool, please feel free to contact yanghliu@redhat.com.

The qa_contact and bug number are as following:
{qa_bugs}

The detailed bug info list is as following:
{bug_info}
"""


EXCEPTION_BUG_REMINDER_MAIL_CONTENT = """
Hi all,
You receive this mail because we have bugs which have exception+/exception? or blocker+/blocker? flag marked for the current release.
(our tool will send this reminder email every Friday morning)
Please review the following bugs and then handle these bugs as soon as possible.


Note:
 1. To get exception/blocker bugs approved, you need:
    - developer to raise exception? or blocker? flag and answer the related questions
    - update the test result from QE to validate the patch in the bug
 2. The ITM setting should not be late than ITM-31 and All the exception+ or blocker+ bugs must be verified by ITM-31.
 3. If your bug is on POST, check with the developer timely about the bug progress.
 4. Once the bug status is on MODIFIED, QE should  add "verified:tested" flag quickly
 5. QE should do the final verification as soon as possible after bug status is ON_QA , and finally setup bug status to VERIFIED.



The qa_contact and bug number are as following:
{qa_bugs}

The detailed bug info list for the bugs with exception+ flag is as following:
{bug_info_1}

The detailed bug info list for the bugs with exception? flag is as following:
{bug_info_2}

The detailed bug info list for the bugs with blocker+ flag is as following:
{bug_info_3}

The detailed bug info list for the bugs with blocker? flag is as following:
{bug_info_4}
"""


QE_TEST_COVERAGE_SUBJECT = "Bugzilla qe_test_coverage flag reminder"
QA_ACK_SUBJECT = "Bugzilla qa_ack flag reminder"
ITM_SETTING_SUBJECT = "Bugzilla ITM setting reminder"
GMAIL_lOG_PATH = "/home/email_content.log"
GMAIL_DEBUG_PATH = "/home/email_debug.log"
EXCEPTION_BUG_REMINDER_SUBJECT = "Bugzilla exception/blocker bugs status reminder"
EXPIRING_ITM_SUBJECT = "Bugzilla expiring ITM reminder"


def build_mail_content(from_addr, to_addrs, cc_addr ,mail_subject ,mail_content):
    msg = MIMEText(_text=mail_content, _subtype="plain", _charset="utf-8")
    msg["Subject"] = Header(s=mail_subject, charset="utf-8")
    msg["From"] = Header(s=from_addr)
    msg["To"] = Header(s=";".join(to_addrs))
    msg["Cc"] = Header(s=";".join(cc_addr))
    msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
    return msg.as_string()


def send_gmail(from_addr, to_addr, cc_addr, mail_subject, mail_content):
    smtp_server = "smtp.corp.redhat.com"
    smtp_port = 587
    msg = build_mail_content(from_addr, to_addr, cc_addr,  mail_subject, mail_content)
    print(msg)
    log_email(GMAIL_lOG_PATH, mail_content)
    
    server = smtplib.SMTP(smtp_server, smtp_port)
    try:
        server.starttls()
        server.set_debuglevel(1)
        server.sendmail(from_addr, to_addr+cc_addr, msg)
    except Exception as err:
        log_email(GMAIL_DEBUG_PATH, str(err))
    finally:
        server.quit()


def log_email(log_path, log_content):
    dir_name = os.path.dirname(log_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(log_path, 'a+') as fd:
        fd.write(str(log_content))

