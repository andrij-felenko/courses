def each_body_own_pass(x, m, v, k, d0, dt):
    """Пастка: для кожного тіла лічимо його силу окремим проходом."""
    n = len(x)
    for i in range(n):
        F = 0.0
        for j in range(n):
            if j == i: continue
            dx = x[i] - x[j]
            r = abs(dx)
            if 0.0 < r < d0:
                F += (k * (d0 - r)) * (dx / r)   # реакцію лічимо ЗАНОВО
        v[i] += F / m[i] * dt
        x[i] += v[i] * dt        # тіло i вже зрушило — наступні бачать НОВЕ x[i]
