import os.path
import base64
import random
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# autentitation function OAuth 2.0
def authenticate_gmail():
    creds = None
    # check if token already exists 
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret_292328750963-rfluhqq3s7u8nova28bo51m9f4pp1lo9.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save token for further use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

# Funkcja to create e-mail message
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

# send e-mail using Gmail API
def send_email(service, sender, to, subject, message_text):
    message = create_message(sender, to, subject, message_text)
    try:
        message = (service.users().messages().send(userId="me", body=message)
                   .execute())
        print(f"Message Id: {message['id']}")
        return message
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# two_step_verification function
def two_step_verification(to):
    # Autoryzuj aplikację
    service = authenticate_gmail()
    # e-maila data
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    print(verification_code)
    sender = "votingsystembus@gmail.com"
    subject = "Your Verification Code - e-voting system"
    message_text = f"Your verification code is: {verification_code}"
    send_email(service, sender, to, subject, message_text)
    return verification_code

def send_vote_confirmation_email(to):
    # Authenticate the application
    service = authenticate_gmail()
    # Email data
    sender = "votingsystembus@gmail.com"
    subject = "Vote Confirmation - e-voting system"
    message_text = f"Thank you for participating in the e-voting system. " \
                   f"Your vote has been successfully recorded.\n\n" \
                   f"Best regards,\nE-voting System Team"
    send_email(service, sender, to, subject, message_text)
    print(f"Confirmation email sent to {to}")


#two_step_verification("emilia.anczarska@gmail.com")