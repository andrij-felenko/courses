def reset(c: BiquadChain) -> None:
    for s in c.stage:
        s.x1 = s.x2 = 0.0
        s.y1 = s.y2 = 0.0

# Повертає True, якщо хвіст згас (фільтр стабільний), інакше False.
def is_stable(c: BiquadChain) -> bool:
    reset(c)
    out = c.step(1.0)                     # імпульс
    peak = abs(out)
    for _ in range(1, 1000):
        out = c.step(0.0)                 # далі — нулі
        peak = max(peak, abs(out))
        if abs(out) > 1e6:                # вибухає
            reset(c)
            return False
    reset(c)
    return abs(out) < 1e-3               # хвіст справді згас
