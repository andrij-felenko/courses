def bias_current(q: Jfet, rs: float) -> float:
    """Струм self-bias-джерела при заданому резисторі витоку.

    Простою ітерацією петлі U_GS = −I·R_S → I(U_GS) за квадратичним
    законом. Петля стискальна, тож збігається за кілька кроків.
    """
    if rs <= 0.0:
        return q.idss                      # закорочений затвор

    i = q.idss                             # старт зверху, з I_DSS
    for _ in range(40):
        ugs = -i * rs                      # напруга, яку дає резистор
        if ugs <= q.vp:
            ugs = q.vp                     # глибше відсічки не буває
        t = 1.0 - ugs / q.vp               # = (1 − U_GS/U_P)
        i = q.idss * t * t                 # струм за квадратичним законом
    return i
