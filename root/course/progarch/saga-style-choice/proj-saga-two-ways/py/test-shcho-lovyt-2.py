def wire_choreography_with_tax(reg, hub, bil, tax):
    bus = Bus()
    async def on_requested(e):  await reg.reserve(e.device_id, e.home_id); await bus.emit("DeviceReserved", e)
    async def on_reserved(e):
        try: await hub.push_config(e.home_id, e.device_id); await bus.emit("DeviceConfigured", e)
        except Exception: await bus.emit("DeviceConfigFailed", e)
    async def on_configured(e):  await tax.register(e.home_id, e.device_id); await bus.emit("DeviceTaxed", e)   # правка 1
    async def on_taxed(e):                                                    # правка 2: білінг слухає вже Taxed
        try: await bil.start_meter(e.home_id, e.device_id)
        except Exception: await bus.emit("DeviceMeterFailed", e)
    async def on_config_failed(e):  await reg.unreserve(e.device_id)
    async def on_meter_failed(e):                                            # ← гілку відкоту tax ТУТ забули
        await hub.wipe_config(e.home_id, e.device_id); await bus.emit("DeviceConfigCompensated", e)
    async def on_config_compensated(e):  await reg.unreserve(e.device_id)
    for ev, fn in [("DeviceReserveRequested", on_requested), ("DeviceReserved", on_reserved),
                   ("DeviceConfigured", on_configured), ("DeviceTaxed", on_taxed),
                   ("DeviceConfigFailed", on_config_failed), ("DeviceMeterFailed", on_meter_failed),
                   ("DeviceConfigCompensated", on_config_compensated)]:
        bus.on(ev, fn)
    return bus

@pytest.mark.asyncio
async def test_choreography_leaks_new_step_in_the_seam():
    reg, hub, bil, tax = Registry(), Hub(), Billing(), Tax()
    bil.down = True
    bus = wire_choreography_with_tax(reg, hub, bil, tax)
    await bus.emit("DeviceReserveRequested", Enroll("home-7", "dev-42"))
    assert reg.reserved == set()                # reserve відкотився
    assert hub.configured == set()              # config відкотився
    assert tax.registered == {"dev-42"}         # ← tax ЛИШИВСЯ: гілку компенсації забули
    # а «статус саги»? спитати ніде — об'єкта саги не існує
