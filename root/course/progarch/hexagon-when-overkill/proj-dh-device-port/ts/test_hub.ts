// test_hub.ts — ті самі shouldHeat і FakeDevice з hub.ts; біжить будь-де
import assert from "node:assert";

// ТЕСТ 1: чисте правило, взагалі без пристрою
assert(shouldHeat(19.9, false));        // холодно — вмикаємо
assert(shouldHeat(20.3, true));         // у смузі й гріли — тримаємо
assert(!shouldHeat(20.6, true));        // перескочили верх — гасимо
assert(!shouldHeat(20.3, false));       // та сама 20.3, та вже вимкнено — НЕ вмикаємо

// ТЕСТ 2: правило проти ПІДРОБКИ, без грама заліза
async function testAgainstFake() {
  const home = new FakeDevice(17.0);     // старт нижче за поріг — дім холодний
  let heating = false;
  for (let i = 0; i < 80; i++) {         // ~40 хв «дому» за частку секунди
    const t = await home.temperature();  // read  — з пам'яті
    heating = shouldHeat(t, heating);    // decide
    await home.heat(heating);            // act   — у журнал, не в реле
    if (t < THRESHOLD)               assert(heating);   // під порогом — тільки гріти
    if (t > THRESHOLD + HYSTERESIS)  assert(!heating);  // над смугою — тільки гасити
  }
  assert.strictEqual(home.log[0], true); // холодний старт → перша дія «ввімкнути»
  assert(home.log.includes(false));      // кімната прогрілась і таки вимкнулась
}
testAgainstFake();
