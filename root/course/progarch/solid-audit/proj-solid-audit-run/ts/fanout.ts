// adapters/fanout.ts — Notifier, що віялом шле в кілька каналів. Сам — теж Notifier.
import type { Notifier } from "../ports";
import type { Message } from "../types";

export class FanoutNotifier implements Notifier {
  constructor(private readonly targets: Notifier[]) {}
  async send(m: Message): Promise<void> {
    await Promise.all(this.targets.map((t) => t.send(m)));
  }
}

// adapters/email.ts — НОВИЙ канал. Новий файл, нова реалізація того ж порту.
import type { Notifier } from "../ports";
import type { Message } from "../types";

export interface Mailer { send(o: { to: string; subject: string; text: string }): Promise<void>; }

export class EmailNotifier implements Notifier {
  constructor(private readonly mailer: Mailer, private readonly to: string) {}
  async send(m: Message): Promise<void> {
    await this.mailer.send({ to: this.to, subject: "Тривога Digital Homes", text: m.body });
  }
}
