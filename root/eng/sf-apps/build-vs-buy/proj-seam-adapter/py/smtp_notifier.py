# adapters/smtp_notifier.py — інший постачальник, ТОЙ САМИЙ порт.
import smtplib
from email.message import EmailMessage

from domain.notifications import Recipient, DomainEvent, NotifyOutcome
from domain.render import render_event

class SmtpNotifier:
    def __init__(self, host: str, port: int, sender: str) -> None:
        self._host, self._port, self._from = host, port, sender

    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome:
        subject, html = render_event(event, to.locale)

        msg = EmailMessage()
        msg["From"] = self._from
        msg["To"] = f"{to.name} <{to.email}>"
        msg["Subject"] = subject
        msg.set_content(html, subtype="html")

        try:
            with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
                smtp.send_message(msg)
            return NotifyOutcome.delivered()
        except smtplib.SMTPRecipientsRefused as e:       # усіх отримувачів відхилено
            code = max(c for c, _ in e.recipients.values())
            return _classify(code)
        except smtplib.SMTPResponseException as e:       # несе .smtp_code
            return _classify(e.smtp_code)
        except OSError as e:                             # мережа / з'єднання
            return NotifyOutcome.retryable(f"smtp io: {e}")

def _classify(code: int) -> NotifyOutcome:
    # 4xx SMTP → тимчасово; 5xx → остаточно. Ті самі два кошики домену.
    if 400 <= code < 500:
        return NotifyOutcome.retryable(f"smtp {code}")
    return NotifyOutcome.rejected(f"smtp {code}")
