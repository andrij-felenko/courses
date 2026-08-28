def drift(phantom_accel, seconds, dt=0.01):
    """Двічі проінтегрувати сталий фальшивий розгін → фальшивий шлях."""
    v = p = 0.0
    for _ in range(int(seconds / dt)):
        v += phantom_accel * dt        # спершу швидкість
        p += v * dt                    # тоді нею — положення
    return p

for deg in (1, 3, 5):
    ph = g * math.sin(deg * DEG)
    print(f"  Δ={deg}°   g·sinΔ = {ph:.3f} м/с²   дрейф за 60 с = {drift(ph, 60):.0f} м")
