# Одне джерело правди: (стан, команда) → новий стан. Чого в таблиці нема — заборонено.
TRANSITIONS = {
    (NEW,     "commission"):  ONLINE,
    (ONLINE,  "markOffline"): OFFLINE,
    (OFFLINE, "markOnline"):  ONLINE,
    (ONLINE,  "retire"):      RETIRED,
    (OFFLINE, "retire"):      RETIRED,
}

def next_state(status, command):
    nxt = TRANSITIONS.get((status, command))
    if nxt is None:
        raise DomainError(f"з «{status}» команда «{command}» неможлива")
    return nxt
