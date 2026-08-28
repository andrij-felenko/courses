import math, random

def expected_conflicts_per_hour(homes, w_per_home_hr, one_way_ms, p_cross):
    lam   = w_per_home_hr / 3600.0        # записів/с в ОДИН ключ
    delta = one_way_ms / 1000.0           # с — одностороння затримка реплікації
    p_gap = 1.0 - math.exp(-lam * delta)  # P(сусідні записи ближче за Δ)
    return homes * w_per_home_hr * p_cross * p_gap

def simulate_one_home(w_per_hr, one_way_ms, p_cross, hours, seed=1):
    """Чесне Монте-Карло: пуассонів потік записів, писар обирається так,
    щоб сусідні відрізнялися з імовірністю p_cross; рахуємо близнюків."""
    rng = random.Random(seed)
    lam, delta, end = w_per_hr / 3600.0, one_way_ms / 1000.0, hours * 3600.0
    t, prev_t, prev_ldr, conflicts = 0.0, None, None, 0
    while True:
        t += rng.expovariate(lam)                       # експоненційний проміжок
        if t > end:
            break
        if prev_ldr is None:
            ldr = rng.randint(0, 1)
        else:
            ldr = (1 - prev_ldr) if rng.random() < p_cross else prev_ldr
        if prev_t is not None and ldr != prev_ldr and (t - prev_t) < delta:
            conflicts += 1                              # різні писарі + в межах Δ → близнюк
        prev_t, prev_ldr = t, ldr
    return conflicts

HOMES, W = 500_000, 120     # пів мільйона домів; активний дім пише у твін раз на 30 с

print("один лідер (серіалізує):     ", 0)
print("мультилідер, дім-пін (p=0):  ", round(expected_conflicts_per_hour(HOMES, W, 80, 0.0)))
for dms in (20, 80, 150):
    print(f"наївний active-active Δ={dms:>3}мс:", round(expected_conflicts_per_hour(HOMES, W, dms, 0.5)))

# звірка формули з Монте-Карло на одному домі
mc = simulate_one_home(W, 80, 0.5, 200_000) / 200_000
an = expected_conflicts_per_hour(1, W, 80, 0.5)
print(f"звірка  MC={mc:.5f}  аналітика={an:.5f}  конфл/дім·год")
