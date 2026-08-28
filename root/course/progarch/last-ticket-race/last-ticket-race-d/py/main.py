def buy_seat(conn, event_id):
    for _ in range(5):                         # кілька спроб
        seats, ver = read_seats(conn, event_id)
        if seats <= 0:
            return "sold_out"
        changed = conn.execute(
            "UPDATE events SET seats_left = seats_left - 1, version = version + 1 "
            "WHERE id = %s AND version = %s", (event_id, ver)).rowcount
        if changed == 1:
            return "ok"                        # версія збіглася — наш запис пройшов
    return "too_busy"                          # надто велика конкуренція
