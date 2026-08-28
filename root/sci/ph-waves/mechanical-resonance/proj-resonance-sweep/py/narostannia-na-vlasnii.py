def run_transient(w, n_periods=80, steps=200):
    T  = 2*np.pi / w
    dt = T / steps
    y  = np.array([0.0, 0.0])
    ts = np.empty(n_periods*steps); xs = np.empty(n_periods*steps)
    for i in range(n_periods*steps):
        ts[i], xs[i] = i*dt, y[0]
        y = rk4_step(y, i*dt, dt, w)
    return ts, xs

ts, xs = run_transient(w0)                # рівно на резонансі
tau = 2 * Q / w0                          # стала наростання, с
print(f"стала наростання τ = 2Q/ω₀ = {tau*1e3:.0f} мс  ≈ {tau/(2*np.pi/w0):.1f} періодів")
