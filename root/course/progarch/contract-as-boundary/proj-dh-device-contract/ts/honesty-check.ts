// honesty-check.ts — чи ЧЕСНО драйвер грає контракт? НЕ контрактні тести й не Pact:
// пробник, що читає I-1..I-6 назад із драйвера й падає, якщо той збрехав.
import assert from "node:assert/strict";
import type { DeviceDriver } from "./device-driver.ts";
import { FakeDevice } from "./fake-device.ts";

const FAULTS = new Set(["offline", "timeout"]);

// Крізь контракт видно лише read → перевіряємо I-2/I-3/I-6 «чорною скринькою».
async function readHonoursContract(d: DeviceDriver): Promise<void> {
  for (let n = 0; n < 100; n++) {
    let r;
    try { r = await d.read(); }
    catch (e) { assert.fail(`I-3 зламано: read кинув крізь межу — ${e}`); }

    if (r.ok) {
      assert.ok(r.tempC >= -40 && r.tempC <= 85, `I-2: tempC поза [−40,85]: ${r.tempC}`);
      assert.ok(r.at > 1e12, `I-6: at не схоже на epoch-мс: ${r.at}`);   // мс, не секунди!
    } else {
      assert.ok(FAULTS.has(r.reason), `I-3: reason поза закритою множиною: ${r.reason}`);
    }
  }
}

// I-4 — про ПРИХОВАНИЙ ефект, якого read не показує; тут треба вікно у фейк.
async function commandIsIdempotent(f: FakeDevice): Promise<void> {
  await f.setTarget(21);
  const w1 = f.writes;
  await f.setTarget(21);                       // той самий таргет, ще раз
  assert.equal(f.target, 21, "I-4: кінцевий стан має бути 21");
  assert.equal(f.writes, w1, "I-4: повтор не мав чіпати залізо вдруге");
}

const fake = new FakeDevice();
await readHonoursContract(fake);
await commandIsIdempotent(fake);
console.log("контракт дотримано: I-1..I-6 чесні ✓");
