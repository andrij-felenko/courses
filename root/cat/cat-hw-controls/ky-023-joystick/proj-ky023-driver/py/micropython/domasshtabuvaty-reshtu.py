# Лінійна пропорція цілими числами, як Arduino map().
def _map(v, from_lo, from_hi, to_lo, to_hi):
    return (v - from_lo) * (to_hi - to_lo) // (from_hi - from_lo) + to_lo

# Сире число осі → −100..+100 із мертвою зоною біля нуля.
def read_axis(a):
    raw = a.pin.read()                         # ADC.read() → сире число
    d = raw - a.center                         # відхилення від центру, знакове

    # 1) мертва зона: близько до центру — це строгий нуль
    if -a.deadzone < d < a.deadzone:
        return 0

    if d > 0:
        # додатний бік: від краю мертвої зони до верхнього краю ходу
        out = _map(d, a.deadzone, a.hi - a.center, 0, 100)
    else:
        # від'ємний бік: від краю мертвої зони до нижнього краю ходу
        out = _map(d, -a.deadzone, a.lo - a.center, 0, -100)

    out = max(-100, min(100, out))             # не вилазити за діапазон
    return -out if a.invert else out           # 3) інверсія осі, якщо треба
