# notify/email_sender.py — ПОРТ. Що системі треба, її словами.
from typing import Protocol

class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None:
        ...

# notify/sendgrid_sender.py — тонкий АДАПТЕР над готовим сервісом.
from sendgrid import SendGridAPIClient        # чужий SDK — лише тут
from sendgrid.helpers.mail import Mail
from .email_sender import EmailSender

class SendgridSender(EmailSender):
    def __init__(self, api_key: str):
        self._client = SendGridAPIClient(api_key)

    def send(self, to: str, subject: str, body: str) -> None:
        msg = Mail(from_email="ops@courier.example",
                   to_emails=to, subject=subject, plain_text_content=body)
        self._client.send(msg)
