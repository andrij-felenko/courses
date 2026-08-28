def tune_step(f_string, f_ref, nudge):
    """Один крок настройки: куди крутити, щоб биття вщухло."""
    now = abs(f_string - f_ref)
    up  = abs((f_string + nudge) - f_ref)   # пробуємо підтягнути вгору
    return f_string + (nudge if up < now else -nudge)

f, nudge = 437.0, 1.0
for _ in range(30):
    f = tune_step(f, 440.0, nudge)
    if abs(f - 440.0) < nudge:               # зайшли в межі кроку
        nudge *= 0.5                         # дрібнимо крок
