// test/notifier.contract.ts — ОДИН контракт на будь-яку реалізацію Notifier
import type { Notifier } from "../ports";
import type { Message } from "../types";

export function notifierContract(
  name: string,
  make: () => { notifier: Notifier; delivered: () => Message[] },
) {
  test(`${name}: доставляє повідомлення, яке прийняв`, async () => {
    const { notifier, delivered } = make();
    const m: Message = { to: "owner", body: "проба" };
    await notifier.send(m);
    expect(delivered()).toContainEqual(m);   // мусить з'явитися у стоці
  });
}

// чесний дублер: сток — його масив. ПРОХОДИТЬ.
notifierContract("RecordingNotifier", () => {
  const n = new RecordingNotifier();
  return { notifier: n, delivered: () => n.sent };
});

// реальний адаптер: сток — «вихідні» фейкового Twilio. ТЕЖ ПРОХОДИТЬ.
class FakeTwilio {
  readonly out: { to: string; from: string; body: string }[] = [];
  messages = { create: async (o: any) => { this.out.push(o); return { sid: "SM_test" }; } };
}
notifierContract("SmsNotifier", () => {
  const fake = new FakeTwilio();
  const n = new SmsNotifier(fake, "+380000000000", "+380111111111");
  // сток адаптера — його вихідні; перекладаємо назад мовою Message
  return { notifier: n, delivered: () => fake.out.map((o) => ({ to: "owner", body: o.body })) };
});

// «мовчазний»: наповнити сток нема чим — ПАДАЄ. Ось як пастку ловлять.
notifierContract("SilentNotifier (пастка)", () => {
  const n = new SilentNotifier();
  return { notifier: n, delivered: () => [] };
});
