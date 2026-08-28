type Handler = (e: Enroll) => Promise<void>;

class Bus {                                  // проста шина подій
  private subs = new Map<string, Handler[]>();
  on(ev: string, fn: Handler) { const a = this.subs.get(ev) ?? []; a.push(fn); this.subs.set(ev, a); }
  async emit(ev: string, e: Enroll) { for (const fn of this.subs.get(ev) ?? []) await fn(e); }
}

function wireChoreography(bus: Bus, registry: Registry, hub: Hub, billing: Billing) {
  // ── ПРЯМА мережа: крок завершив — кинув подію, наступний підхопив ──
  bus.on("DeviceReserveRequested", async e => {
    await registry.reserve(e.deviceId, e.homeId);
    await bus.emit("DeviceReserved", e);                 // хто підхопить — реєстр не знає
  });
  bus.on("DeviceReserved", async e => {
    try { await hub.pushConfig(e.homeId, e.deviceId); await bus.emit("DeviceConfigured", e); }
    catch { await bus.emit("DeviceConfigFailed", e); }   // впав — запускаємо відкіт
  });
  bus.on("DeviceConfigured", async e => {
    try { await billing.startMeter(e.homeId, e.deviceId); }   // останній крок: тиша = «готово»
    catch { await bus.emit("DeviceMeterFailed", e); }
  });

  // ── КОМПЕНСАЦІЙНА мережа: окремі підписки, що їдуть НАЗАД ──
  bus.on("DeviceConfigFailed", async e => {              // упав крок 2 → відкотити крок 1
    await registry.unreserve(e.deviceId);
  });
  bus.on("DeviceMeterFailed", async e => {               // упав крок 3 → відкотити крок 2…
    await hub.wipeConfig(e.homeId, e.deviceId);
    await bus.emit("DeviceConfigCompensated", e);        // …і лише тоді ланцюг іде далі назад
  });
  bus.on("DeviceConfigCompensated", async e => {         // …→ відкотити крок 1
    await registry.unreserve(e.deviceId);
  });
}
