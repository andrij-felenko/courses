// adapters/sendgrid-notifier.ts — ЄДИНЕ місце зі словом "SendGrid".
import { Notifier, Recipient, DomainEvent, NotifyOutcome } from "../domain/notifications";
import { renderEvent } from "../domain/render";   // ТЕКСТ листа — рішення домену

const ENDPOINT = "https://api.sendgrid.com/v3/mail/send";

export class SendGridNotifier implements Notifier {
  constructor(private apiKey: string, private from: string) {}

  async notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome> {
    const { subject, html } = renderEvent(event, to.locale);

    // Переклад ДОМЕН → чужий формат тіла живе тут і тільки тут.
    const body = {
      personalizations: [{ to: [{ email: to.email, name: to.name }] }],
      from: { email: this.from },
      subject,
      content: [{ type: "text/html", value: html }],
    };

    let resp: Response;
    try {
      resp = await fetch(ENDPOINT, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });
    } catch (e) {
      // навіть збій мережі НЕ протікає як є — це доменний "варто повторити"
      return { status: "retryable", reason: `network: ${(e as Error).message}` };
    }

    // Переклад чужих КОДІВ → доменний наслідок. 202/429/5xx назовні не йдуть.
    if (resp.status === 202) return { status: "delivered" };
    if (resp.status === 429 || resp.status >= 500)
      return { status: "retryable", reason: `sendgrid ${resp.status}` };
    return { status: "rejected", reason: `sendgrid ${resp.status}` };
  }
}
