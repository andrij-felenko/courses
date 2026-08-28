import math

def simulate_standing_wave(length_m=1.0, nodes=200, wave_speed=100.0, 
                           freq_hz=150.0, steps=1000, boundary="fixed"):
    """
    Симуляція 1D стоячої хвилі методом скінченних різниць (FDTD).
    boundary: 'fixed' (жорстка межа) або 'free' (вільний кінець)
    """
    dx = length_m / (nodes - 1)
    # Обираємо dt з умови Куранта C = v * dt / dx = 0.8 <= 1.0
    courant = 0.8
    dt = courant * dx / wave_speed
    c_sq = courant * courant

    u_prev = [0.0] * nodes
    u_curr = [0.0] * nodes
    u_next = [0.0] * nodes

    # Масив для накопичення максимальних амплітуд (обвідна стоячої хвилі)
    envelope = [0.0] * nodes

    omega = 2.0 * math.pi * freq_hz

    for step in range(steps):
        t = step * dt

        # Джерело синусоїдальних коливань на лівому кінці (x = 0)
        u_curr[0] = math.sin(omega * t)

        # Перерахунок внутрішніх вузлів струни
        for i in range(1, nodes - 1):
            laplacian = u_curr[i + 1] - 2.0 * u_curr[i] + u_curr[i - 1]
            u_next[i] = 2.0 * u_curr[i] - u_prev[i] + c_sq * laplacian

        # Гранична умова на правому кінці (x = L)
        if boundary == "fixed":
            u_next[nodes - 1] = 0.0  # Нерухомий вузол
        elif boundary == "free":
            u_next[nodes - 1] = u_next[nodes - 2]  # Пучність

        # Оновлення обвідної та зсув часових шарів
        for i in range(nodes):
            envelope[i] = max(envelope[i], abs(u_next[i]))
            u_prev[i] = u_curr[i]
            u_curr[i] = u_next[i]

    # Пошук вузлів та пучностей у сформованій обвідній
    nodes_found = [i for i in range(1, nodes - 1) if envelope[i] < 0.05]
    antinodes_found = [i for i in range(1, nodes - 1) if envelope[i] > 1.8]

    return {
        "dx": dx,
        "dt": dt,
        "nodes_count": len(nodes_found),
        "antinodes_count": len(antinodes_found),
        "max_envelope": max(envelope)
    }

if __name__ == "__main__":
    res_fixed = simulate_standing_wave(boundary="fixed")
    print(f"Жорсткі межі: максимум обвідної = {res_fixed['max_envelope']:.2f}, "
          f"знайдено вузлів = {res_fixed['nodes_count']}")
    
    res_free = simulate_standing_wave(boundary="free")
    print(f"Вільна межа: максимум обвідної = {res_free['max_envelope']:.2f}, "
          f"знайдено пучностей = {res_free['antinodes_count']}")
