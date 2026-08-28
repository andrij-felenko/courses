def shutdown(m, state):
    """Акуратно завершитись: роззброїти (ЛИШЕ на землі!) і закрити лінію."""
    try:
        if m is not None and state.link_alive():
            # disarm тільки якщо апарат озброєний І на землі — інакше це падіння!
            if state.armed and state.alt_m < 0.5:
                print("[EXIT] апарат на землі — роззброюю")
                m.mav.command_long_send(
                    m.target_system, m.target_component,
                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                    0, 0, 0, 0, 0, 0, 0, 0)   # param1 = 0 → disarm
            else:
                print("[EXIT] апарат у польоті або стан невідомий — НЕ чіпаю")
    finally:
        if m is not None:
            m.close()                          # завжди звільняємо лінію
        print("[EXIT] з'єднання закрито")
