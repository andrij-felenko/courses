# test_hub.py — ті самі should_heat і FakeDevice з hub.py; біжить будь-де

def test_rule_holds_the_band():          # ТЕСТ 1: чисте правило, взагалі без пристрою
    assert should_heat(19.9, heating=False)       # холодно — вмикаємо
    assert should_heat(20.3, heating=True)        # у смузі й гріли — тримаємо
    assert not should_heat(20.6, heating=True)    # перескочили верх — гасимо
    assert not should_heat(20.3, heating=False)   # та сама 20.3, та вже вимкнено — НЕ вмикаємо
    # два останні рядки — одна температура, різні відповіді: оце й є пам'ять, що глушить клацання

def test_rule_against_the_fake():        # ТЕСТ 2: правило проти ПІДРОБКИ, без грама заліза
    home = FakeDevice(start=17.0)        # старт нижче за поріг — дім холодний
    heating = False
    for _ in range(80):                  # ~40 хв життя «дому» за частку секунди
        t = home.temperature()           # read  — з пам'яті, не з давача
        heating = should_heat(t, heating) # decide
        home.heat(heating)               # act   — у журнал, не в реле
        # інваріант гістерезису мусить триматися НА КОЖНОМУ такті:
        if t < THRESHOLD:                assert heating       # під порогом — тільки гріти
        if t > THRESHOLD + HYSTERESIS:   assert not heating   # над смугою — тільки гасити
    assert home.log[0] is True           # холодний старт → перша ж дія «ввімкнути»
    assert False in home.log             # кімната прогрілась і таки вимкнулась
