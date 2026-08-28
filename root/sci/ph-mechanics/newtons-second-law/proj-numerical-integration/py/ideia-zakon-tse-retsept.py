import numpy as np

def euler(r, v, accel, dt):
    """Один крок явного Ейлера. accel(r, v) → прискорення від стану."""
    a = accel(r, v)
    return r + v * dt, v + a * dt          # ОБИДВА оновлення — зі СТАРИХ значень

def semi_implicit(r, v, accel, dt):
    """Напівнеявний Ейлер: усього один переставлений рядок проти явного."""
    a = accel(r, v)
    v_new = v + a * dt                      # спершу оновлюємо швидкість…
    return r + v_new * dt, v_new            # …а положення веземо вже НОВОЮ швидкістю
