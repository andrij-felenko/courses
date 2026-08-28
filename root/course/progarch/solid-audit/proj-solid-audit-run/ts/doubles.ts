// test/doubles.ts — чесні дублери для тестів
import type { Notifier, Clock } from "../ports";
import type { Message } from "../types";

export class RecordingNotifier implements Notifier {
  readonly sent: Message[] = [];
  async send(m: Message): Promise<void> { this.sent.push(m); }   // записує прийняте
}
export class FixedClock implements Clock {
  constructor(private readonly at: Date) {}
  now(): Date { return this.at; }
}

// test/policy.test.ts — політику видно судити в ізоляції
import { AlarmPolicy } from "../policy";
import { RecordingNotifier, FixedClock } from "./doubles";

const at = new Date(2026, 6, 11, 23, 5);   // застиглий час: 23:05

test("кіт у pet-safe не піднімає тривоги", async () => {
  const spy = new RecordingNotifier();
  const policy = new AlarmPolicy(spy, new FixedClock(at));
  policy.arm();
  await policy.handle({ type: "motion", zone: "pet-safe" });
  expect(spy.sent).toHaveLength(0);        // жодного повідомлення — і жодного SMS
});

test("рух в охоронюваній зоні шле рівно одну тривогу з часом", async () => {
  const spy = new RecordingNotifier();
  const policy = new AlarmPolicy(spy, new FixedClock(at));
  policy.arm();
  await policy.handle({ type: "motion", zone: "hallway" });
  expect(spy.sent).toEqual([{ to: "owner", body: "Рух у зоні «hallway» о 23:05" }]);
});

test("роззброєний дім мовчить", async () => {
  const spy = new RecordingNotifier();
  const policy = new AlarmPolicy(spy, new FixedClock(at));   // arm() не викликаємо
  await policy.handle({ type: "motion", zone: "hallway" });
  expect(spy.sent).toHaveLength(0);
});
