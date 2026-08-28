import { test, expect } from "vitest";

// той самий рушій runSaga; додаємо КРОК tax між config і meter
function enrollSteps(reg: Registry, hub: Hub, bil: Billing, tax: Tax, home: string, dev: string): Step[] {
  return [
    step("reserve", () => reg.reserve(dev, home),       () => reg.unreserve(dev)),
    step("config",  () => hub.pushConfig(home, dev),     () => hub.wipeConfig(home, dev)),
    step("tax",     () => tax.register(home, dev),       () => tax.unregister(dev)),   // ← ОДИН новий рядок
    step("meter",   () => bil.startMeter(home, dev),     () => bil.stopMeter(home, dev)),
  ];
}

test("оркестрація: новий крок tax відкочується зворотним порядком — ДАРМА", async () => {
  const reg = new Registry(), hub = new Hub(), bil = new Billing(), tax = new Tax();
  bil.down = true;                                    // збій на останньому кроці
  const store = new Store();
  await expect(runSaga("s1", enrollSteps(reg, hub, bil, tax, "home-7", "dev-42"), store))
    .rejects.toThrow();
  expect(reg.reserved.size).toBe(0);                 // reserve відкотився
  expect(hub.configured.size).toBe(0);               // config відкотився
  expect(tax.registered.size).toBe(0);               // ← tax теж — хоч ми компенсацій НЕ дописували
  expect(store.load("s1")!.status).toBe("compensated");   // а статус саги — ось він, однією викличкою
});
