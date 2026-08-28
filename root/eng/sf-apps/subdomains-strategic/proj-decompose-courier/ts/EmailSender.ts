// notify/EmailSender.ts — ПОРТ. Що системі треба, її словами.
export interface EmailSender {
  send(to: string, subject: string, body: string): Promise<void>;
}

// notify/SendgridSender.ts — тонкий АДАПТЕР над готовим сервісом.
import { EmailSender } from "./EmailSender";
import sgMail from "@sendgrid/mail"; // чужий SDK — лише тут

export class SendgridSender implements EmailSender {
  constructor(apiKey: string) { sgMail.setApiKey(apiKey); }

  async send(to: string, subject: string, body: string): Promise<void> {
    await sgMail.send({ to, from: "ops@courier.example", subject, text: body });
  }
}
