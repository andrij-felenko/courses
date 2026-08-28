// thermostat.test.ts — женемо крізь шов підробки. decide НЕ редагуємо.
import { test } from "node:test";
import assert from "node:assert/strict";
import { decide, type Sensor, type Heater } from "./thermostat.ts";

class FakeSensor implements Sensor {
  constructor(private readonly reads: number) {}
  read(): number { return this.reads; }                  // завжди заготовлене
}

class SpyHeater implements Heater {
  readonly calls: string[] = [];
  on(): void { this.calls.push("on"); }
  off(): void { this.calls.push("off"); }
}

test("холодно → вмикаємо", () => {
  const spy = new SpyHeater();
  decide(new FakeSensor(19.0), spy, 20.0);               // 19.0 < 20.0
  assert.deepEqual(spy.calls, ["on"]);
});

test("тепло → вимикаємо", () => {
  const spy = new SpyHeater();
  decide(new FakeSensor(21.0), spy, 20.0);               // 21.0 ≥ 20.0
  assert.deepEqual(spy.calls, ["off"]);
});

test("рівно поріг → НЕ гріємо", () => {
  const spy = new SpyHeater();
  decide(new FakeSensor(20.0), spy, 20.0);               // 20.0 < 20.0 хибно
  assert.deepEqual(spy.calls, ["off"]);                  // «<» строгий
});
