def integrate_delay(k, tau_d, x0, dt, T):
    """dx/dt = −k·x(t − τ_d). Історію тримаємо у списку-буфері."""
    n = int(round(T / dt))
    d = int(round(tau_d / dt))          # затримка, поміряна в кроках
    x = np.empty(n + 1); x[0] = x0
    hist = [x0] * (d + 1)               # минуле до старту вважаємо сталим x0
    for i in range(n):
        x_past = hist[-d - 1]           # x, виміряний τ_d = d·dt тому
        x[i + 1] = x[i] + dt * (-k * x_past)
        hist.append(x[i + 1])
    return np.linspace(0.0, n * dt, n + 1), x
