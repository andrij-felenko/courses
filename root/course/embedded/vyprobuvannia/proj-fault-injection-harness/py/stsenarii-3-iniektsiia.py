def test_clock_step_backward_resilience(harness):
    ntp = harness["ntp"]
    collector = harness["collector"]
    collector.clear()

    # 1. Початкова синхронізація з точним часом
    ntp.set_time_shift(0.0)
    time.sleep(5.0)

    # 2. Ін'єкція зсуву на 3600 секунд назад
    ntp.set_time_shift(-3600.0)
    time.sleep(10.0)

    with collector.lock:
        msgs = list(collector.received_messages)

    assert len(msgs) >= 3, "Вузол припинив генерацію телеметрії після стрибка часу назад"

    # Перевірка: інтервали генерації монотонного часу (uptime) залишаються додатними
    uptimes = [m["payload"].get("uptime_ms", 0) for m in msgs]
    for i in range(len(uptimes) - 1):
        delta = uptimes[i+1] - uptimes[i]
        assert delta > 0, f"Виявлено немонотонний крок таймера: delta = {delta} мс"
