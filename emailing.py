'''
* In python folder (venv?) should see "Install Certificates.command
* run this file and SSLCertVerificationError should go away"
'''

from email.message import EmailMessage
import ssl
import smtplib
import logging

import logs
from random import randint
from time import sleep

from file_helpers import read_first_line

BEN = 'ben'
JOHN = 'john'
BOTH = 'both'
SUBJ_STD = 'Automated msg: an exception occurred'
SUBJ_PARAM = 'Automated msg: parameter exception occurred'


class Email():
    def __init__(self, receiver_file, subject, body):
        self.sender = read_first_line('email-sender')
        self.password = read_first_line('email-password')
        self.receiver = read_first_line(receiver_file)
        self.msg = EmailMessage()
        self.msg['From'] = self.sender
        self.msg['To'] = self.receiver
        self.msg['Subject'] = subject
        self.msg.set_content(body)
        self.context = ssl.create_default_context()


def send_email_if_desired(email_recip, subject, body):
    if email_recip is None or body is None:
        return
    if subject is None:
        subject = SUBJ_STD
    if email_recip == JOHN:
        send_email_to_john(subject, body)
    if email_recip == BEN:
        send_email_to_me(subject, body)
    if email_recip == BOTH:
        send_email_to_both(subject, body)


def send_email_to_john(subject, body):
    send_email(Email('email-john', subject, body))


def send_email_to_me(subject, body):
    send_email(Email('email-ben', subject, body))


def send_email(email : Email):
    try:
        send_email_ssl(email)
    except Exception as e:
        send_email_wo_ssl(email)
        stack = logs.get_final_stack_trace(e)
        logging.warning(f'Email sent without use of SSL due to the following error:\n{stack}')


def send_email_ssl(email : Email):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=email.context) as smtp:
        smtp.login(email.sender, email.password)
        smtp.sendmail(email.sender, email.receiver, email.msg.as_string())


def send_email_wo_ssl(email : Email):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email.sender, email.password)
    server.sendmail(email.sender, email.receiver, email.msg.as_string())
    server.close()


def send_email_to_both(subject, body):
    send_email_to_john(subject, 'Ben was also notified of the following error:\n\n' + body)
    send_email_to_me(subject, 'John was also notified of the following error:\n\n' + body)


# def main():
#     print(send_email_to_both('b', 'foo'))

# if __name__ == "__main__":
#     main()