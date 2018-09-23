import logging
import smtplib

# we import the Twilio client from the dependency we just installed
from twilio.rest import Client

logger = logging.getLogger(__name__)

class TwilioSMS():
    from_number = "+XXX"
    def __init__(self, account_sid, auth_token, target_number):
        self.client = Client(account_sid, auth_token)
        self.target_number = target_number

    def send_message(self, body):
        self.client.messages.create(to=self.target_number,
                               from_=self.from_number,
                               body=body)

class GMail():
    def __init__(self, gmail_user, gmail_pass, to_addr):
        self.gmail_user = gmail_user
        self.gmail_pass = gmail_pass
        self.to_addr = to_addr if type(to_addr) is list else [to_addr]

    def send_email(self, subject, body):
        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (self.gmail_user, ", ".join(self.to_addr), subject, body)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(self.gmail_user, self.gmail_pass)
            server.sendmail(self.gmail_user, self.to_addr, message)
            server.close()
            logger.info('Successfully sent mail!')
        except:
            logger.error("Failed to send mail!")

        logger.debug(message)
