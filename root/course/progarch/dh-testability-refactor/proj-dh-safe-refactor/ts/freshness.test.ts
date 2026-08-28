// freshness.test.ts — характеризація: пришпилюємо ВАДУ, зелену вже сьогодні
import { test, expect } from "vitest";
import { Reading, Config, tick } from "./hub";

class FakeSensor {                              // фейк: віддає задані виміри, один за одним
  private q: Reading[];
  constructor(...readings: Reading[]) { this.q = readings; }
  read(): Reading { return this.q.shift()!; }
}
class SpyHeater {                               // шпигун: нічого не гріє, лише пам'ятає виклики
  calls: string[] = [];
  on()  { this.calls.push("on"); }
  off() { this.calls.push("off"); }
}

test("застиглий давач гріє вічно — TODAY", () => {
  const heater = new SpyHeater();
  const stuck = new FakeSensor(...Array(5).fill({ celsius: 19.9, ok: true }));
  for (let i = 0; i < 5; i++) tick(stuck, heater, { threshold: 20.0 });
  expect(heater.calls).toEqual(["on", "on", "on", "on", "on"]);  // v1 гріє вічно
});
