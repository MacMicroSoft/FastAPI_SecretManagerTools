from re import TEMPLATE
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.email_utils import DefaultChecker
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi_mail.errors import ConnectionErrors

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_PORT=os.getenv('MAIL_PORT'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

