def bias_current(q: Jfet, rs: float) -> float:
    if rs <= 0.0:
        return q.idss

    i = q.idss * 0.5                       # старт із середини діапазону
    for _ in range(60):
        ugs = -i * rs
        if ugs <= q.vp:
            ugs = q.vp
        t = 1.0 - ugs / q.vp
        i_new = q.idss * t * t
        i = 0.5 * (i + i_new)              # демпфування — гасить гойдання
    return i
