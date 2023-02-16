import os
import logging
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
from pyisemail import is_email


logging.basicConfig(level='INFO',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

load_dotenv('.env.dev')

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


def check_email(email_address: str) -> bool:
    """Checks if the email address is valid"""
    if is_email(email_address):
        return True
    else:
        logging.warning(f"Email address {email_address} is not valid")


def get_recipients(emails_file: str) -> list[str]:
    """Collects email addresses from the file and
    puts them in the list if they are valid"""
    recipients_list = []
    try:
        with open(emails_file, 'r') as f:
            logging.info(f"Collecting emails from {emails_file}...")
            for line in f:
                line = line.rstrip('\n')
                if check_email(line):
                    recipients_list.append(line)
        if recipients_list:
            logging.info(f"Collected {len(recipients_list)} email(s) from {emails_file}")
            return recipients_list
        else:
            logging.warning(f"No emails collected from {emails_file}")
    except FileNotFoundError:
        logging.warning(f"File {emails_file} does not exist")


def get_text(text_file: str) -> tuple[str, str]:
    """
    Reads email text from the file.
    Returns the first line of the file as the email subject
    and the remaining lines as the email body.
    """
    try:
        with open(text_file, 'r') as f:
            subject = f.readline().strip("\n")
            data = f.readlines()[1:]
            body = "".join(data)
            if body:
                logging.info(f"Collected email subject and text from {text_file}")
                return subject, body
            else:
                logging.warning(f"No email text in {text_file}")
    except FileNotFoundError:
        logging.warning(f"File {text_file} does not exist")


@app.route("/send-mail")
def index() -> str:
    """
    Main function of the application.
    Collects email subject and text, sender and recipients email addresses.
    If there is enough data, sends emails to the recipients.
    """
    sender = os.getenv('MAIL_USERNAME')
    recipients_file = os.getenv('RECIPIENTS_FILE')
    text_file = os.getenv('TEXT_FILE')

    recipients = get_recipients(recipients_file)
    subject, body = get_text(text_file)

    if sender and recipients and body:
        with mail.connect() as conn:
            for recipient in recipients:
                msg = Message(subject,
                              sender=sender,
                              recipients=[recipient],
                              body=body)
                logging.info(f"Sending notifications to {recipient}")
                conn.send(msg)
            info_message = f"Message sent to {len(recipients)} email(s)"
            logging.info(info_message)
            return info_message
    else:
        logging.warning("No emails were sent")
        return "No emails were sent"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
