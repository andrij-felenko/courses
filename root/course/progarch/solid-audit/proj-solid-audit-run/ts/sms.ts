// adapters/sms.ts — увесь Twilio замкнено ТУТ.
import type { Notifier } from "../ports";
import type { Message } from "../types";

// Мінімальна форма клієнта Twilio, якою ми користуємось. Справжній клієнт її задовольняє,
// а в тесті адаптера можна підставити фейковий HTTP — сам адаптер теж стає тестованим.
export interface TwilioLike {
  messages: { create(o: { to: string; from: string; body: string }): Promise<{ sid: string }> };
}

export class SmsNotifier implements Notifier {
  constructor(private readonly client: TwilioLike,
              private readonly ownerPhone: string,
              private readonly fromPhone: string) {}

  async send(m: Message): Promise<void> {
    // Тут — і тільки тут — логічний «owner» перетворюється на номер, а Message — на SMS.
    await this.client.messages.create({ to: this.ownerPhone, from: this.fromPhone, body: m.body });
  }
}

// adapters/push.ts — інший канал, той самий вузький порт.
import type { Notifier } from "../ports";
import type { Message } from "../types";

export interface PushChannel { push(deviceTag: string, text: string): Promise<void>; }

export class PushNotifier implements Notifier {
  constructor(private readonly channel: PushChannel, private readonly deviceTag: string) {}
  async send(m: Message): Promise<void> { await this.channel.push(this.deviceTag, m.body); }
}

// adapters/clock.ts — системний годинник як адаптер порту Clock.
import type { Clock } from "../ports";
export class SystemClock implements Clock { now(): Date { return new Date(); } }
