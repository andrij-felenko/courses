def drain_link(m, state):
    """Забрати ВСЕ, що накопичилось на лінії з минулого такту.
    Не блокує: щойно черга порожня, recv_match повертає None — виходимо."""
    while True:
        msg = m.recv_match(blocking=False)
        if msg is None:
            break                      # черга вичерпана — виходимо з циклу
        handle_message(m, state, msg)  # обробляємо кожен кадр по черзі


def handle_message(m, state, msg):
    """Одне місце, куди сходяться всі вхідні повідомлення."""
    mtype = msg.get_type()

    if mtype == 'BAD_DATA':
        # парсер спіткнувся на пошкоджених байтах — НЕ помилка лінії,
        # просто завади. Тихо пропускаємо; наступні кадри зберуться.
        return

    if mtype == 'HEARTBEAT':
        # серцебиття апарата — оновлюємо позначку «востаннє чули»
        state.last_heartbeat = time.time()
        state.armed = bool(msg.base_mode
                           & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

    elif mtype == 'GLOBAL_POSITION_INT':
        state.alt_m = msg.relative_alt / 1000.0   # мм → м
        state.lat = msg.lat / 1e7
        state.lon = msg.lon / 1e7

    elif mtype == 'SYS_STATUS':
        state.batt_v = msg.voltage_battery / 1000.0   # мВ → В
