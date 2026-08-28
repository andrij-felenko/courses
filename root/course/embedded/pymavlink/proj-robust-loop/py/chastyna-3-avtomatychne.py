RECONNECT_MIN_S = 0.5     # перша пауза між спробами
RECONNECT_MAX_S = 5.0     # стеля паузи (backoff далі не росте)


def connect(device, state):
    """Одна спроба підключитись і дочекатися апарата.
    Повертає живий об'єкт з'єднання або None. НІКОЛИ не блокує назавжди."""
    try:
        m = mavutil.mavlink_connection(device)
    except Exception as e:
        print("[CONN] не вдалось відкрити %s: %s" % (device, e))
        return None

    # чекаємо heartbeat З ТАЙМАУТОМ — без нього зависли б навіки на мертвій лінії
    hb = m.wait_heartbeat(timeout=RECONNECT_MAX_S)
    if hb is None:
        m.close()             # КРИТИЧНО: не лишаємо витік дескриптора
        return None

    # wait_heartbeat щойно ДОВІВ, що лінія жива, — чесно стамкнемо це в стан.
    # Без цього наступний такт побачив би last_heartbeat=None → «мертво» і зчинив
    # би хибну тривогу з негайним реконектом (churn після кожного відновлення).
    state.last_heartbeat = time.time()
    print("[CONN] апарат на лінії: sys %d, comp %d"
          % (m.target_system, m.target_component))
    return m


def reconnect(device, old, state):
    """Закрити стару лінію (проти витоку) і піднімати нову з backoff."""
    if old is not None:
        try:
            old.close()        # ПЕРШ НІЖ відкрити нову — закрити стару!
        except Exception:
            pass               # уже мертва — байдуже, головне звільнити fd

    delay = RECONNECT_MIN_S
    while True:
        m = connect(device, state)
        if m is not None:
            return m
        print("[CONN] не вдалось; повтор через %.1f с" % delay)
        time.sleep(delay)                       # єдиний свідомий sleep — коли лінії НЕМАЄ
        delay = min(delay * 2, RECONNECT_MAX_S) # backoff: пауза росте до стелі
