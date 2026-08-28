// main.ts — композиційний корінь. Єдине місце збирання графа.
import twilio from "twilio";
import { AlarmPolicy } from "./policy";
import { SmsNotifier } from "./adapters/sms";
import { SystemClock } from "./adapters/clock";
import type { SensorEvent } from "./types";

export function buildPolicy(): AlarmPolicy {
  // Ось тут — і ніде більше — читаємо секрети й будуємо конкретне.
  const client = twilio(process.env.TWILIO_SID!, process.env.TWILIO_TOKEN!);
  const sms    = new SmsNotifier(client, process.env.OWNER_PHONE!, process.env.TWILIO_FROM!);
  const clock  = new SystemClock();

  const policy = new AlarmPolicy(sms, clock);   // деталі впорснуто в ядро
  policy.arm();
  return policy;
}

// десь у старті: підписуємо політику на потік подій із давачів
function wire(bus: { on(ev: "sensor", cb: (e: SensorEvent) => void): void }) {
  const policy = buildPolicy();
  bus.on("sensor", (ev) => { void policy.handle(ev); });
}
