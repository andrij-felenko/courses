// tests/fitness/presence-retention.test.ts
import { Twin, RETENTION_MS } from "../../twin";

test("присутність не зберігається довше вікна", () => {
  const twin = new Twin();
  const now = Date.UTC(2026, 6, 11, 12);              // місяць 0-базований: 6 = липень
  twin.record(now - 48 * 3_600_000, true);           // два дні тому
  twin.record(now - 1  * 3_600_000, false);          // година тому
  twin.prune(now);
  const kept = twin.presenceSince(now - 3650 * 86_400_000);   // за десятиліття
  expect(kept.every(e => e.ts >= now - RETENTION_MS)).toBe(true);
  expect(kept.length).toBe(1);
});
