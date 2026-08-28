import { vi } from "vitest";

test("характеризація: продовження із запізненням", () => {
  vi.useFakeTimers();                                        // ← шов: точка вмикання ззовні
  vi.setSystemTime(new Date(Date.UTC(2026, 2, 3, 9, 0)));
  try {
    const sub: Subscription = { id: "s-1", planPrice: 100, paidUntil: utc(2026, 3, 1) };
    const r = renew(sub);
    expect(r.status).toBe("ok");
    expect(r.amount).toBe(102);
    expect(sub.paidUntil).toEqual(utc(2026, 4, 2, 9));        // ← ФАКТ, а не бажане
  } finally {
    vi.useRealTimers();
  }
});
