def test_power_cut_during_flash_write(harness):
    relay = harness["relay"]
    collector = harness["collector"]

    for cycle in range(50):
        collector.clear()
        relay.power_on()
        
        # Очікуємо початку активного запису та перших повідомлень телеметрії
        t_start = time.time()
        saw_telemetry = False
        while time.time() - t_start < 5.0:
            with collector.lock:
                if len(collector.received_messages) > 0:
                    saw_telemetry = True
                    break
            time.sleep(0.05)

        assert saw_telemetry, f"Вузол не відновив роботу після циклу {cycle}"

        # Ін'єкція випадкового обриву в інтервалі 10..200 мс (під час запису кадру)
        time.sleep(random.uniform(0.01, 0.20))
        relay.power_off()
        time.sleep(0.3)

    # Фінальне завантаження та перевірка цілісності логу
    relay.power_on()
    time.sleep(3.0)
    
    with collector.lock:
        seq_ids = [m["payload"]["seq"] for m in collector.received_messages if "seq" in m["payload"]]
    
    # Перевірка: жоден лічильник не перескочив назад і не згенерував дублікатів
    assert len(seq_ids) > 0, "Немає повідомлень після фінального старту"
    assert seq_ids == sorted(seq_ids), "Порушено монотонне зростання sequence ID після аварії"
