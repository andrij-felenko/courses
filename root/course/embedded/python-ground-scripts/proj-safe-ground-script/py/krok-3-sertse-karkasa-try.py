def cleanup(m, v):
    """Привести апарат у безпеку й закрити лінію. Викликається при БУДЬ-ЯКОМУ виході."""
    try:
        if m is not None and v.link_alive() and v.armed and v.on_ground():
            # роззброюємо ЛИШЕ якщо апарат озброєний І стоїть на землі
            print("[EXIT] апарат на землі й озброєний — роззброюю")
            m.mav.command_long_send(
                m.target_system, m.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0,                       # confirmation
                0, 0, 0, 0, 0, 0, 0)     # param1 = 0 → disarm (звичайний, не форсований)
        else:
            print("[EXIT] у польоті / стан невідомий / лінія мертва — НЕ чіпаю мотори")
    finally:
        if m is not None:
            m.close()                    # завжди звільняємо лінію (порт/сокет)
        print("[EXIT] з'єднання закрито")


def main():
    m = mavutil.mavlink_connection(CONN)
    v = Vehicle()
    m.wait_heartbeat()
    print("апарат на лінії: sys %d, comp %d" % (m.target_system, m.target_component))

    try:
        while True:
            msg = m.recv_match(blocking=True, timeout=1.0)
            if msg is not None:
                v.on_message(msg)        # оновлюємо знімок стану
            # …тут твоя логіка керування, що спирається на v…

    except KeyboardInterrupt:
        print("\n[EXIT] Ctrl+C — акуратне завершення")
    finally:
        cleanup(m, v)                    # ← ось воно: спрацює хай як ми вийшли
