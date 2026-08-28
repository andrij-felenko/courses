interface Clock  { now(): number; }
interface Store  { recent(): Reading[]; }
interface Cooler { turnOn(): void; turnOff(): void; }

class CoolingController {
  constructor(private clock: Clock, private store: Store,
              private cooler: Cooler, private policy: Policy) {}
  tick(): void {
    const d = decideCooling(this.store.recent(), this.clock.now(), this.policy);
    d === "on" ? this.cooler.turnOn() : this.cooler.turnOff();
  }
}

// три тривіальні дублі — кожен рівно за своїм гачком:
class FakeClock implements Clock { now() { return 1_000_000; } }        // недетермінований → фейк
class FakeStore implements Store {                                      // тримає стан → фейк
  recent() { return [{ at: 1_000_000 - 60_000, celsius: 26 },
                     { at: 1_000_000 - 10_000, celsius: 27 }]; }
}
class SpyCooler implements Cooler {                                     // незворотний ефект → шпигун
  readonly calls: string[] = [];
  turnOn()  { this.calls.push("on");  }
  turnOff() { this.calls.push("off"); }
}

test("спека у вікні → контролер вмикає охолодження", () => {
  const spy = new SpyCooler();
  new CoolingController(new FakeClock(), new FakeStore(), spy,
                        { threshold: 25, windowMs: 5 * 60_000 }).tick();
  assert.deepEqual(spy.calls, ["on"]);                     // перевірка взаємодії
});
