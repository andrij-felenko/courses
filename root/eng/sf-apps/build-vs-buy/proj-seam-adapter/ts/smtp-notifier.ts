// adapters/smtp-notifier.ts — інший постачальник, ТОЙ САМИЙ порт.
import { Transporter } from "nodemailer";
import { Notifier, Recipient, DomainEvent, NotifyOutcome } from "../domain/notifications";
import { renderEvent } from "../domain/render";

export class SmtpNotifier implements Notifier {
  constructor(private tx: Transporter, private from: string) {}

  async notify(to: Recipient, event: DomainEvent): Promise<NotifyOutcome> {
    const { subject, html } = renderEvent(event, to.locale);
    try {
      await this.tx.sendMail({
        from: this.from,
        to: `${to.name} <${to.email}>`,
        subject,
        html,
      });
      return { status: "delivered" };
    } catch (err: any) {
      const code: number | undefined = err.responseCode;   // код відповіді SMTP
      if (code === undefined) return { status: "retryable", reason: `smtp io: ${err.code}` };
      // 4xx SMTP → тимчасово; 5xx → остаточно. Ті самі два кошики домену.
      if (code >= 400 && code < 500) return { status: "retryable", reason: `smtp ${code}` };
      return { status: "rejected", reason: `smtp ${code}` };
    }
  }
}
