def steady_amplitude(w, n_settle=60, n_measure=20, steps=200):
    """Амплітуда сталих коливань на частоті w (рад/с)."""
    T  = 2*np.pi / w
    dt = T / steps                       # steps кроків на період — з запасом для RK4
    y  = np.array([0.0, 0.0])
    t  = 0.0
    for _ in range(n_settle * steps):    # дати перехідному процесу згаснути
        y = rk4_step(y, t, dt, w); t += dt
    xmax, xmin = -1e30, 1e30             # виміряти розмах на усталеній ділянці
    for _ in range(n_measure * steps):
        y = rk4_step(y, t, dt, w); t += dt
        xmax, xmin = max(xmax, y[0]), min(xmin, y[0])
    return (xmax - xmin) / 2

ratios = np.arange(0.30, 1.70 + 1e-9, 0.01)      # ω / ω₀ від 0.3 до 1.7
A  = np.array([steady_amplitude(r * w0) for r in ratios])
A0 = F0 / k                                       # статичний прогин = 62.5 мкм

i_peak = np.argmax(A)
print(f"пік на ω/ω₀ = {ratios[i_peak]:.2f}   f = {ratios[i_peak]*w0/(2*np.pi):.1f} Гц")
print(f"підсилення на піку A/A₀ = {A[i_peak]/A0:.1f}   (очікувано ≈ Q = {Q:.0f})")
print(f"амплітуда на піку = {A[i_peak]*1e3:.2f} мм")
