import pytest

# той самий рушій run_saga; додаємо КРОК tax між config і meter
def enroll_steps(reg, hub, bil, tax, home, dev):
    return [
        Step("reserve", lambda: reg.reserve(dev, home),        lambda: reg.unreserve(dev)),
        Step("config",  lambda: hub.push_config(home, dev),    lambda: hub.wipe_config(home, dev)),
        Step("tax",     lambda: tax.register(home, dev),       lambda: tax.unregister(dev)),   # ← ОДИН новий рядок
        Step("meter",   lambda: bil.start_meter(home, dev),    lambda: bil.stop_meter(home, dev)),
    ]

@pytest.mark.asyncio
async def test_orchestration_rolls_back_new_step_for_free():
    reg, hub, bil, tax = Registry(), Hub(), Billing(), Tax()
    bil.down = True                                    # збій на останньому кроці
    store = Store()
    with pytest.raises(RuntimeError):
        await run_saga("s1", enroll_steps(reg, hub, bil, tax, "home-7", "dev-42"), store)
    assert reg.reserved == set()                       # reserve відкотився
    assert hub.configured == set()                     # config відкотився
    assert tax.registered == set()                     # ← tax теж — хоч ми компенсацій НЕ дописували
    assert store.load("s1")["status"] == "compensated" # а статус саги — ось він, однією викличкою
