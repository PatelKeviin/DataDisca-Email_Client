import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
from pathlib import Path


class EmailClient:
    """ An email client to send emails.
    """

    def __init__(self, server: str, server_port: int, user_name: str, password: str):
        """ Class constructor to initialise EmailClient

        Parameters:
        server (str): Email server used by the user
        server_port (int): Port number of the email server
        user_name (str): Email address
        password (str): Email password
            """

        # Email credentials
        self.user_name = user_name
        self.__password = password

        # used to add plain texts/HTML parts in the email
        self.__email_content = MIMEMultipart()
        # add sender's info
        self.__email_content['From'] = user_name
        # uses SMTP email protocol to communicate with email service provider
        self.__mail_server = smtplib.SMTP(
            host=server, port=server_port)

        # necessary for internal workings
        self.__is_subject_added = False
        self.__is_body_added = False
        self.__is_attached = False
        self.__is_signature_added = False

    def set_subject(self, subject: str):
        """ Method to set subject for the email (optional).

        Parameters:
        subject (str): Email subject to set
            """

        self.__is_subject_added = (subject is not None and subject != '')
        if self.__is_subject_added:
            self.__email_content['Subject'] = subject

    def set_body(self, body: str):
        """ Method to set body for the email (optional).

        Parameters:
        body (str): Email body to set
            """

        self.__is_body_added = (body is not None and body != '')
        if self.__is_body_added:
            self.__email_content.attach(MIMEText(body, 'plain'))

    def set_signature(self, signature: str):
        """ Method to set signature for the email (optional).

        Parameters:
        signature (str): Email signature to set
            """

        self.__is_signature_added = (signature is not None and signature != '')
        if self.__is_signature_added:
            self.__email_content.attach(MIMEText(signature, 'plain'))

    def add_attachment(self, attachment_path: str):
        """ Method to attach attachments in the email (optional).

        Parameters:
        attachment_path (str): Path of attachment
            """

        attachment = MIMEBase('application', "octet-stream")

        with open(attachment_path, 'rb') as file:
            attachment.set_payload(file.read())

        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition',
                              'attachment; filename="{}"'.format(Path(attachment_path).name))

        self.__email_content.attach(attachment)

        # added attachment
        self.__is_attached = True

    def send(self, recipient: str) -> bool:
        """ Method to send email message.

        Parameters:
        recipient (str): Recipient's email address

        Returns:
        bool: Determines success of email being sent
            """
        if self.__is_attached and not self.__is_subject_added:
            print('Error: Subject is empty. Please add a subject and send again.')
            return False

        if not self.__is_subject_added and not self.__is_body_added and not self.__is_signature_added:
            print('Error: Cannot send empty email message. Please add at least one from subject, body or signature.')
            return False

        self.__email_content['To'] = recipient
        self.__email_content['Date'] = formatdate(localtime=True)

        try:
            self.__mail_server.starttls()   # start a secure TLS connection
            # login with user credentials on email server
            self.__mail_server.login(self.user_name, self.__password)

            # send email message
            self.__mail_server.send_message(self.__email_content)

            return True
        except Exception as e:
            print('Something went wrong :(\n', e)

            return False
        finally:
            # close connection with email server
            self.__mail_server.quit()

    def reset_email(self):
        """ Resets all email content except for the initialisation details.
            """

        # used to add plain texts/HTML parts in the email
        self.__email_content = MIMEMultipart()
        # add sender's info
        self.__email_content['From'] = self.user_name

        # necessary for internal workings
        self.__is_subject_added = False
        self.__is_body_added = False
        self.__is_attached = False
        self.__is_signature_added = False


if __name__ == "__main__":
    # using Google mail server
    mail_server = 'smtp.gmail.com'
    port_number = 587
    # sender's credentials
    username = 'khushbup1010@gmail.com'
    with open('password.txt', 'r') as pass_file:
        email_password = pass_file.read()
    # recipient's email addr
    email_recipient = 'kevin.patel@ai.datadisca.com'

    # Email message content
    # linux command for creating text files for processor and memory usage each
    os.system('cat /proc/cpuinfo >> processor.txt')
    os.system('cat /proc/meminfo >> memory.txt')
    # linux command for creating a text file for running processes
    os.system('ps -aux >> running_process.txt')

    # Email subject
    email_subject = 'Server Performance'

    # Email body
    email_body = '-------------- CPU INFO --------------\n'
    with open('processor.txt', 'r') as processor_file:
        for line in processor_file.readlines():
            email_body += line

    email_body += '------------ MEMORY INFO ------------\n'
    with open('memory.txt') as memory_file:
        for line in memory_file.readlines():
            email_body += line

    # Email signature
    email_signature = '\n\nKind regards,\nkevinmanojpatel@gmail.com'

    # using 'EmailClient' class for sending email messages
    email_client = EmailClient(mail_server, port_number, username, email_password)
    email_client.set_subject(email_subject)
    email_client.set_body(email_body)
    email_client.set_signature(email_signature)
    email_client.add_attachment('running_process.txt')

    # sending email
    if email_client.send(email_recipient):
        print('Email sent.')
    else:
        print('Failed :(')
