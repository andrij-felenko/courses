from functools import reduce

# ЗАПИС: дописати факт. Лог сам присвоює позицію — вона й є порядок.
def record(log, home_id, cmd):
    log.append(home_id, {
        "type": "Locked" if cmd["kind"] == "lock" else "Unlocked",
        "seq": cmd["seq"], "by": cmd["by"],
    })                                 # durable: fsync до підтвердження

# ЧИТАННЯ: поточний стан = згортка журналу. «Як зараз» рахуємо, а не зберігаємо.
def apply(s, e):
    return LockState(
        bolt="locked" if e["type"] == "Locked" else "unlocked",
        version=s.version + 1,
        last_cmd=f"{e['by']}#{e['seq']}",
    )
def project(events):
    return reduce(apply, events, LockState())
