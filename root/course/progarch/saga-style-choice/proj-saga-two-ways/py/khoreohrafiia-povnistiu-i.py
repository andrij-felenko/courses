class Bus:                                   # проста шина подій
    def __init__(self): self.subs = {}
    def on(self, ev, fn): self.subs.setdefault(ev, []).append(fn)
    async def emit(self, ev, e):
        for fn in list(self.subs.get(ev, [])): await fn(e)

def wire_choreography(bus, registry, hub, billing):
    # ── ПРЯМА мережа: крок завершив — кинув подію, наступний підхопив ──
    async def on_requested(e):
        await registry.reserve(e.device_id, e.home_id)
        await bus.emit("DeviceReserved", e)                 # хто підхопить — реєстр не знає
    async def on_reserved(e):
        try:
            await hub.push_config(e.home_id, e.device_id); await bus.emit("DeviceConfigured", e)
        except Exception:
            await bus.emit("DeviceConfigFailed", e)          # впав — запускаємо відкіт
    async def on_configured(e):
        try:
            await billing.start_meter(e.home_id, e.device_id)   # останній крок: тиша = «готово»
        except Exception:
            await bus.emit("DeviceMeterFailed", e)

    # ── КОМПЕНСАЦІЙНА мережа: окремі підписки, що їдуть НАЗАД ──
    async def on_config_failed(e):                          # упав крок 2 → відкотити крок 1
        await registry.unreserve(e.device_id)
    async def on_meter_failed(e):                           # упав крок 3 → відкотити крок 2…
        await hub.wipe_config(e.home_id, e.device_id)
        await bus.emit("DeviceConfigCompensated", e)        # …і лише тоді ланцюг іде далі назад
    async def on_config_compensated(e):                     # …→ відкотити крок 1
        await registry.unreserve(e.device_id)

    bus.on("DeviceReserveRequested", on_requested)
    bus.on("DeviceReserved", on_reserved)
    bus.on("DeviceConfigured", on_configured)
    bus.on("DeviceConfigFailed", on_config_failed)
    bus.on("DeviceMeterFailed", on_meter_failed)
    bus.on("DeviceConfigCompensated", on_config_compensated)
