ACCEPTED, RETRY, UNSUPPORTED, REFUSED, SILENCE = range(5)

_VERDICT = {mav.MAV_RESULT_ACCEPTED:             ACCEPTED,
            mav.MAV_RESULT_TEMPORARILY_REJECTED: RETRY,
            mav.MAV_RESULT_UNSUPPORTED:          UNSUPPORTED}


def send_order(link, param5, value, hold_s, wait=0.06):
    link.mav.command_long_send(
        link.target_system, AUTOPILOT,
        mav.MAV_CMD_ACTUATOR_TEST, 0,
        value,       # param1 — уставка: 0…1 мотор, −1…1 серва, NaN — відпустити
        hold_s,      # param2 — термін утримання, секунди
        0, 0,
        param5,      # param5 — кого крутити
        0, 0)

    if wait <= 0:
        return SILENCE
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        m = link.recv_match(type='COMMAND_ACK', blocking=True, timeout=0.02)
        if m is None or m.command != mav.MAV_CMD_ACTUATOR_TEST:
            continue
        return _VERDICT.get(m.result, REFUSED)
    return SILENCE                        # не «погано», а «поки що невідомо»


def standard_function(px4_function):
    """Стандартна нумерація MAVLink адресує лише мотори й серви."""
    if 101 <= px4_function <= 112:
        return px4_function - 101 + 1
    if 201 <= px4_function <= 215:
        return px4_function - 201 + 33
    return -1                             # шасі, захват, камера — запасного ходу немає
