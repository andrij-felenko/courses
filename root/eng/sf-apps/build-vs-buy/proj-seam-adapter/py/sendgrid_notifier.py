# adapters/sendgrid_notifier.py — єдине місце зі словом "SendGrid".
import json
import urllib.error
import urllib.request

from domain.notifications import Notifier, Recipient, DomainEvent, NotifyOutcome
from domain.render import render_event      # ТЕКСТ листа — рішення домену

ENDPOINT = "https://api.sendgrid.com/v3/mail/send"

class SendGridNotifier:                      # структурно реалізує Notifier (Protocol)
    def __init__(self, api_key: str, sender: str) -> None:
        self._api_key = api_key
        self._from = sender

    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome:
        subject, html = render_event(event, to.locale)

        # Переклад ДОМЕН → чужий формат тіла живе тут і тільки тут.
        body = {
            "personalizations": [{"to": [{"email": to.email, "name": to.name}]}],
            "from": {"email": self._from},
            "subject": subject,
            "content": [{"type": "text/html", "value": html}],
        }
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code                    # 4xx/5xx приходять сюди
        except urllib.error.URLError as e:
            return NotifyOutcome.retryable(f"network: {e.reason}")

        # Переклад чужих КОДІВ → доменний наслідок. 202/429/5xx назовні не йдуть.
        if code == 202:
            return NotifyOutcome.delivered()
        if code == 429 or code >= 500:
            return NotifyOutcome.retryable(f"sendgrid {code}")
        return NotifyOutcome.rejected(f"sendgrid {code}")
