def simulate(m, k, c, x0=0.0, v0=0.0, T=3.0, fs=2000.0):
    """RK4-інтегрування m·ẍ + c·ẋ + k·x = 0. Стан s = [x, v]."""
    w0 = np.sqrt(k / m); two_zw = c / m            # c/m = 2ζω₀
    def deriv(s):
        x, v = s
        return np.array([v, -w0 * w0 * x - two_zw * v])
    dt = 1.0 / fs; n = int(T * fs); t = np.arange(n) * dt
    s = np.array([x0, v0]); out = np.empty(n)
    for i in range(n):
        out[i] = s[0]
        k1 = deriv(s); k2 = deriv(s + 0.5 * dt * k1)
        k3 = deriv(s + 0.5 * dt * k2); k4 = deriv(s + dt * k3)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, out

def c_for_zeta(m, k, zeta):
    """Коефіцієнт демпфера під заданий ζ: c = 2ζ·√(m·k)."""
    return 2.0 * zeta * np.sqrt(m * k)

# Чверть кузова: m = 300 кг, k = 30000 Н/м. Який c дає бажаний ζ?
m, k = 300.0, 30000.0
print("c критичне (ζ=1) =", c_for_zeta(m, k, 1.0), "Н·с/м")
print("c для ζ = 0.3    =", c_for_zeta(m, k, 0.3), "Н·с/м")

# Симулюємо кузов після поштовху й «міряємо» ζ з двох перших вершин
t, x = simulate(m, k, c_for_zeta(m, k, 0.3), x0=0.0, v0=0.5)
idx, _ = find_peaks(x, height=0.02 * np.max(np.abs(x)))
p1, p2 = x[idx[0]], x[idx[1]]
delta = np.log(p1 / p2)
zeta = delta / np.sqrt(4 * np.pi**2 + delta**2)
print(f"дві вершини: {p1:.4f} → {p2:.4f}  →  δ={delta:.3f}, ζ={zeta:.3f}, Q={1/(2*zeta):.2f}")
