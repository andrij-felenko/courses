// wiring.test.ts
import { describe, it, expect } from "vitest";
import { tick, type Config } from "./home";
import { FakeSensor, SpyHeater } from "./doubles";

const CFG: Config = { threshold: 20.0 };

describe("tick докручує проводку", () => {
  it("холодний вимір вмикає розетку", () => {
    const heater = new SpyHeater();
    tick(new FakeSensor({ celsius: 18.0, ok: true }), heater, CFG);
    expect(heater.calls).toEqual(["on"]);
  });

  it("теплий вимір вимикає розетку", () => {
    const heater = new SpyHeater();
    tick(new FakeSensor({ celsius: 22.0, ok: true }), heater, CFG);
    expect(heater.calls).toEqual(["off"]);
  });

  it("мертвий давач вимикає розетку", () => {
    const heater = new SpyHeater();
    tick(new FakeSensor({ celsius: 5.0, ok: false }), heater, CFG);
    expect(heater.calls).toEqual(["off"]);   // холодно, та вірити нема чому
  });

  it("кожен оберт докручує свою команду", () => {
    const heater = new SpyHeater();
    const sensor = new FakeSensor(
      { celsius: 18.0, ok: true },
      { celsius: 22.0, ok: true },
      { celsius: 19.0, ok: true },
    );
    for (let i = 0; i < 3; i++) tick(sensor, heater, CFG);
    expect(heater.calls).toEqual(["on", "off", "on"]);
  });
});
