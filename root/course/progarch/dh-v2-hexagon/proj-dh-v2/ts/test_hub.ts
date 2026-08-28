// test_hub.ts — ганяємо сервіс підробками: без заліза, без бази, без sleep
import assert from "node:assert";

// ДОКАЗ 0: зведене ядро тримає смугу
{
  const cfg = { threshold: 20.0 };
  assert(decide({ celsius: 19.9, ok: true }, cfg, false));    // холодно — вмикаємо
  assert(decide({ celsius: 20.3, ok: true }, cfg, true));     // у смузі й гріли — тримаємо
  assert(!decide({ celsius: 20.6, ok: true }, cfg, true));    // перескочили верх — гасимо
  assert(!decide({ celsius: 20.3, ok: true }, cfg, false));   // та сама 20.3, вимкнено — НЕ вмикаємо
  assert(!decide({ celsius: NaN, ok: false }, cfg, true));    // німий давач → спокій
}

// ДОКАЗ 1 і 2: одна правда + HTTP задарма
{
  const sensor = new FakeSensor(21.0), heater = new FakeHeater();   // 21 °C > поріг 20
  const hub = new HubService(sensor, heater, new InMemoryDeviceRepository(), { threshold: 20.0 });

  hub.tick();                                    // двері 1: 21 над порогом — не гріємо
  assert.strictEqual(hub.state().heating, false);
  assert.deepStrictEqual(heater.log, []);

  hub.setThreshold(25.0);                         // двері 2: CLI підняв поріг
  hub.addDevice({ kind: "lock", room: "спальня", state: "unknown" });

  hub.tick();                                     // двері 1: наступний тік бачить нову правду
  const snap = hub.state();
  assert.strictEqual(snap.heating, true);         // 21 < 25 → цикл тепер гріє
  assert.deepStrictEqual(heater.log, [true]);     // реле ввімкнулось рівно раз
  assert(snap.devices.some((d) => d.room === "спальня"));   // CLI-пристрій видно циклу

  const httpGetState = (h: HubService): HomeSnapshot => h.state();  // двері 3 — HTTP
  assert.strictEqual(httpGetState(hub).heating, true);             // нуль правок ядра
}
