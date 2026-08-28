// dispatcher.ts — «до». Один клас робить усе одразу.
import twilio from "twilio";
import * as fs from "node:fs";

export class AlarmDispatcher {
  private armed = false;
  arm()    { this.armed = true; }
  disarm() { this.armed = false; }

  handle(ev: SensorEvent): void {
    // 1) політика: чи це взагалі тривога?
    if (ev.type !== "motion" || !this.armed) return;
    if (ev.zone === "pet-safe") return;                    // зона, де бігає кіт

    // 2) як це звучить для людини
    const t = new Date().toLocaleTimeString();
    const text = `Рух у зоні «${ev.zone}» о ${t}`;

    // 3) чим шлемо — Twilio SMS, створений тут-таки з ключами з оточення
    const client = twilio(process.env.TWILIO_SID!, process.env.TWILIO_TOKEN!);
    client.messages.create({
      to: process.env.OWNER_PHONE!, from: process.env.TWILIO_FROM!, body: text,
    });

    // 4) слід — теж прибитий цвяхом, синхронний запис у файл
    fs.appendFileSync("/var/log/alarms.log", text + "\n");
  }
}
