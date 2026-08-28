def test_network_blackout_and_replay_drain(harness):
    chaos = harness["chaos"]
    collector = harness["collector"]
    collector.clear()

    # 1. Повна ізоляція вузла на 30 секунд
    chaos.set_blackout()
    time.sleep(30.0)

    # Під час обриву повідомлення не повинні доходити до брокера
    with collector.lock:
        assert len(collector.received_messages) == 0, "Дані просочуються крізь ізольований лінк"

    # 2. Відновлення каналу
    chaos.clear()
    
    # 3. Очікування отримання поточних вимірів (Live) та вивантаження накопичених (Replay)
    drain_timeout = 60.0
    t_start = time.time()
    live_msgs = []
    replay_msgs = []

    while time.time() - t_start < drain_timeout:
        with collector.lock:
            live_msgs = [m for m in collector.received_messages if m["topic"].endswith("/state")]
            replay_msgs = [m for m in collector.received_messages if m["topic"].endswith("/replay")]
        
        # Вузол має вивантажити щонайменше 15 накопичених точок
        if len(replay_msgs) >= 15 and len(live_msgs) >= 5:
            break
        time.sleep(0.5)

    assert len(live_msgs) > 0, "Свіжий потік (Live) заблоковано чергою повторів"
    assert len(replay_msgs) >= 15, f"Отримано лише {len(replay_msgs)} записів з офлайн-буфера"

    # Перевірка неперервності послідовності в архіві
    replay_seqs = [m["payload"]["seq"] for m in replay_msgs]
    for i in range(len(replay_seqs) - 1):
        assert replay_seqs[i+1] == replay_seqs[i] + 1, (
            f"Розрив у черзі повторів: {replay_seqs[i]} -> {replay_seqs[i+1]}"
        )
