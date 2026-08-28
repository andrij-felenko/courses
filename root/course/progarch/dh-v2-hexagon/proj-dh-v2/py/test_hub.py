# test_hub.py — ганяємо сервіс підробками: без заліза, без бази, без sleep

def test_core_holds_the_band():          # ДОКАЗ 0: зведене ядро тримає смугу
    cfg = Config(threshold=20.0)
    assert decide(Reading(19.9), cfg, heating=False)          # холодно — вмикаємо
    assert decide(Reading(20.3), cfg, heating=True)           # у смузі й гріли — тримаємо
    assert not decide(Reading(20.6), cfg, heating=True)       # перескочили верх — гасимо
    assert not decide(Reading(20.3), cfg, heating=False)      # та сама 20.3, вимкнено — НЕ вмикаємо
    assert not decide(Reading(float("nan"), ok=False), cfg, heating=True)  # німий давач → спокій

def test_both_doors_share_one_truth():   # ДОКАЗ 1 і 2: одна правда + HTTP задарма
    sensor, heater = FakeSensor(celsius=21.0), FakeHeater()   # 21 °C — тепліше за поріг 20
    hub = HubService(sensor, heater, InMemoryDeviceRepository(), Config(threshold=20.0))

    hub.tick()                                    # двері 1: тік — 21 над порогом, не гріємо
    assert hub.state().heating is False
    assert heater.log == []                       # реле жодного разу не смикнулось

    hub.set_threshold(25.0)                        # двері 2: та сама мить — CLI підняв поріг
    hub.add_device(Device("lock", "спальня"))      # двері 2: CLI додав пристрій

    hub.tick()                                     # двері 1: наступний тік БАЧИТЬ нову правду
    snap = hub.state()
    assert snap.heating is True                    # 21 < 25 → цикл тепер гріє
    assert heater.log == [True]                    # і реле ввімкнулось рівно раз
    assert any(d.room == "спальня" for d in snap.devices)   # CLI-пристрій видно циклу

    def http_get_state(h: HubService) -> HomeSnapshot:   # двері 3 — HTTP, завтра
        return h.state()                                 # той самий виклик, нуль правок ядра
    assert http_get_state(hub).heating is True
