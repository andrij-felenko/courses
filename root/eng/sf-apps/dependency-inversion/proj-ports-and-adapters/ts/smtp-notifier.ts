// infra/smtp-notifier.ts ── ЄДИНЕ місце, що знає SMTP. Мапить домен ↔ лист.
import { Order } from "../domain/order";
import { Notifier } from "../domain/ports";

export class SmtpNotifier implements Notifier {
  constructor(private readonly smtp: Smtp, private readonly from: string) {}

  async orderPlaced(o: Order): Promise<void> {
    await this.smtp.send({
      from: this.from,
      to: o.email,                                   // домен дав пошту — SMTP її вживає
      subject: `Замовлення ${o.id} прийнято`,
      text: `Дякуємо! Сума до сплати: ${o.total()} грн.`,
    });
  }
}
