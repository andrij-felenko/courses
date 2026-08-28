def grad(interior, dt):
    """∇S по внутрішніх точках: −m·(дискретне прискорення + g)·Δt."""
    x = np.concatenate(([x_start], interior, [x_end]))
    accel = (x[2:] - 2*x[1:-1] + x[:-2]) / dt**2   # друга різниця = ẍ у вузлах
    return -m * (accel + g) * dt

interior = np.zeros(N - 1)          # старт: усі внутрішні точки на землі
alpha = 0.3 * dt / m                # темп спуску
for _ in range(20000):
    interior -= alpha * grad(interior, dt)
