function wireChoreographyWithTax(reg: Registry, hub: Hub, bil: Billing, tax: Tax): Bus {
  const bus = new Bus();
  bus.on("DeviceReserveRequested", async e => { await reg.reserve(e.deviceId, e.homeId); await bus.emit("DeviceReserved", e); });
  bus.on("DeviceReserved", async e => {
    try { await hub.pushConfig(e.homeId, e.deviceId); await bus.emit("DeviceConfigured", e); }
    catch { await bus.emit("DeviceConfigFailed", e); }
  });
  bus.on("DeviceConfigured", async e => { await tax.register(e.homeId, e.deviceId); await bus.emit("DeviceTaxed", e); });  // правка 1
  bus.on("DeviceTaxed", async e => {                                                     // правка 2: білінг слухає вже Taxed
    try { await bil.startMeter(e.homeId, e.deviceId); }
    catch { await bus.emit("DeviceMeterFailed", e); }
  });
  bus.on("DeviceConfigFailed", async e => { await reg.unreserve(e.deviceId); });
  bus.on("DeviceMeterFailed", async e => {                                              // ← гілку відкоту tax ТУТ забули
    await hub.wipeConfig(e.homeId, e.deviceId); await bus.emit("DeviceConfigCompensated", e);
  });
  bus.on("DeviceConfigCompensated", async e => { await reg.unreserve(e.deviceId); });
  return bus;
}

test("хореографія: той самий доданий крок ТЕЧЕ у шві — тест це й ловить", async () => {
  const reg = new Registry(), hub = new Hub(), bil = new Billing(), tax = new Tax();
  bil.down = true;
  const bus = wireChoreographyWithTax(reg, hub, bil, tax);
  await bus.emit("DeviceReserveRequested", { homeId: "home-7", deviceId: "dev-42" });
  expect(reg.reserved.size).toBe(0);            // reserve відкотився
  expect(hub.configured.size).toBe(0);          // config відкотився
  expect(tax.registered.has("dev-42")).toBe(true);   // ← tax ЛИШИВСЯ: гілку компенсації забули
  // а «статус саги»? спитати ніде — об'єкта саги не існує
});
