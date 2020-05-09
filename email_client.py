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

        self.__server = server
        self.__server_port = server_port
        self.__user_name = user_name
        self.__password = password

        # used to add plain texts/HTML parts in the email
        self.__email_content = MIMEMultipart()
        # add sender's info
        self.__email_content['From'] = user_name

    def set_subject(self, subject: str):
        """ Method to set subject for the email (optional).

        Parameters:
        subject (str): Email subject to set
            """

        self.__email_content['Subject'] = subject
        self.__is_subject_added = True

    def set_body(self, body: str):
        """ Method to set body for the email (optional).

        Parameters:
        body (str): Email body to set
            """

        self.__email_content.attach(MIMEText(body, 'plain'))
        self.__is_body_added = True

    def set_signature(self, signature: str):
        """ Method to set signature for the email (optional).

        Parameters:
        signature (str): Email signature to set
            """

        self.__email_content.attach(MIMEText(signature, 'plain'))
        self.__is_signature_added = True

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
            # uses SMTP email protocol to communicate with email service provider
            self.__mail_server = smtplib.SMTP(
                host=self.__server, port=self.__server_port)
            self.__mail_server.starttls()   # start a secure TLS connection
            # login with user credentials on email server
            self.__mail_server.login(self.__user_name, self.__password)

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
        self.__email_content['From'] = self.__user_name


if __name__ == "__main__":

    # using Google mail server
    server = 'smtp.gmail.com'
    port_number = 587
    # sender's credentials
    username = 'kevinmanojpatel@gmail.com'
    password = ''
    with open('password.txt', 'r') as pass_file:
        password = pass_file.read()
    # recipient's email addr
    recipient = 'khushbup1010@gmail.com'

    # Email message content
    # linux command for creating text files for processer and memory usage each
    os.system('cat /proc/cpuinfo >> processor.txt')
    os.system('cat /proc/meminfo >> memory.txt')
    # linux command for creating a text file for running processes
    os.system('ps -aux >> running_process.txt')

    # Email subject
    subject = 'Server Performance'

    # Email body
    body = '-------------- CPU INFO --------------\n'
    with open('processor.txt', 'r') as file:
        for line in file.readlines():
            body += line

    body += '------------ MEMORY INFO ------------\n'
    with open('memory.txt') as file:
        for line in file.readlines():
            body += line

    # Email signature
    signature = '\n\nKind regards,\nkevin.patel@ai.datadisca.com'

    # using 'EmailClient' class for sending email messages
    email_client = EmailClient(server, port_number, username, password)
    email_client.set_subject(subject)
    email_client.set_body(body)
    email_client.set_signature(signature)
    email_client.add_attachment('running_process.txt')

    # sending email
    if email_client.send(recipient):
        print('Email sent.')
    else:
        print('Failed :(')
