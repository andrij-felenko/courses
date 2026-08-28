// test/ocp.test.ts — той самий AlarmPolicy, новий канал, ані рядка змін у ядрі
import { AlarmPolicy } from "../policy";
import { FanoutNotifier } from "../adapters/fanout";
import { RecordingNotifier, FixedClock } from "./doubles";

test("email додається без правок політики", async () => {
  const sms   = new RecordingNotifier();      // за ними в тесті — будь-які канали
  const email = new RecordingNotifier();
  const policy = new AlarmPolicy(
    new FanoutNotifier([sms, email]), new FixedClock(new Date(2026, 6, 11, 23, 5)),
  );
  policy.arm();
  await policy.handle({ type: "motion", zone: "hallway" });
  expect(sms.sent).toHaveLength(1);
  expect(email.sent).toHaveLength(1);         // новий канал отримав тривогу
});
