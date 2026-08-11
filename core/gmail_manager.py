import base64
import os

from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


CREDENTIALS_FILE = "data/credentials.json"
TOKEN_FILE = "data/gmail_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(
                TOKEN_FILE,
                SCOPES
            )
        except Exception as error:
            print("Gmail token load error:", error)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())

            except Exception as error:
                print("Gmail token refresh error:", error)
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    "Could not find data/credentials.json"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        os.makedirs(
            "data",
            exist_ok=True
        )

        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8"
        ) as token:
            token.write(
                creds.to_json()
            )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


def send_email(to_email, subject, body):
    try:
        service = get_gmail_service()

        message = EmailMessage()

        message["To"] = to_email
        message["Subject"] = subject

        message.set_content(body)

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        gmail_message = {
            "raw": encoded_message
        }

        result = (
            service.users()
            .messages()
            .send(
                userId="me",
                body=gmail_message
            )
            .execute()
        )

        print(
            "Email sent. Message ID:",
            result.get("id")
        )

        return True

    except HttpError as error:
        print("Gmail API error:", error)
        return False

    except Exception as error:
        print("Gmail error:", error)
        return False