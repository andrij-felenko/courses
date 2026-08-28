import numpy as np
from scipy.signal import find_peaks

def make_ringdown(fs=2000.0, T=4.0, f_d=45.0, zeta=0.05, A=1.0,
                  phi=0.0, noise=0.01, seed=0):
    """Синтез запису вільного дзвону з відомими параметрами + шум.
    Потрібен, щоб перевіряти оцінювач: знаємо правду — бачимо похибку."""
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, T, 1.0 / fs)
    w_d = 2 * np.pi * f_d
    gamma = zeta * w_d / np.sqrt(1 - zeta**2)      # γ = ζ·ω₀, ω₀ = ω_d/√(1−ζ²)
    x = A * np.exp(-gamma * t) * np.cos(w_d * t + phi)
    return t, x + noise * rng.standard_normal(t.size)

def rough_freq(a, fs):
    """Груба частота дзвону з піка спектра — щоб знати, як далеко стоять вершини."""
    A = np.abs(np.fft.rfft(a - np.mean(a)))
    f = np.fft.rfftfreq(len(a), 1.0 / fs)
    return f[1 + np.argmax(A[1:])]                 # пропускаємо нульову (сталу) складову

def refine_peak(a, i):
    """Параболою по трьох точках уточнюємо вершину між відліками:
    повертає (зсув у частках кроку, справжню висоту вершини)."""
    y0, y1, y2 = a[i - 1], a[i], a[i + 1]
    den = y0 - 2 * y1 + y2
    if den == 0:
        return 0.0, y1
    d = 0.5 * (y0 - y2) / den                      # |d| < 0.5 — де насправді вершина
    return d, y1 - 0.25 * (y0 - y2) * d

def estimate_damping(t, a):
    fs = 1.0 / (t[1] - t[0])
    noise_rms = np.std(a[int(0.9 * len(a)):])      # хвіст запису = сам шум
    f0 = rough_freq(a, fs)
    dist = max(1, int(0.6 * fs / f0))              # вершини не ближче за пів періоду
    amax = np.max(np.abs(a))
    floor = max(0.04 * amax, 6 * noise_rms)        # довіряємо лише виразним вершинам
    idx, _ = find_peaks(a, distance=dist, height=floor)
    idx = idx[(idx > 0) & (idx < len(a) - 1)]

    tp, ap = [], []
    for i in idx:                                  # уточнюємо кожну вершину параболою
        d, apk = refine_peak(a, i)
        tp.append(t[i] + d / fs); ap.append(apk)
    tp, ap = np.array(tp), np.array(ap)
    if len(ap) < 3:
        raise ValueError("замало вершин — довший запис або менший шум")

    T_d = np.mean(np.diff(tp)); w_d = 2 * np.pi / T_d          # частота — з кроку вершин
    slope, _ = np.polyfit(tp, np.log(ap), 1, w=ap)             # пряма крізь ln(вершини),
    gamma = -slope                                             # вага ∝ висота (великим віри більше)

    w0 = np.hypot(gamma, w_d)                                  # ω₀ = √(γ² + ω_d²) — без m, k!
    zeta = gamma / w0
    Q = w0 / (2 * gamma)

    delta = np.log(ap[0] / ap[-1]) / (len(ap) - 1)             # перехресна перевірка:
    zeta_ld = delta / np.sqrt(4 * np.pi**2 + delta**2)         # лог-декремент по краях

    return dict(f_d=w_d / (2 * np.pi), gamma=gamma, w0=w0,
                zeta=zeta, Q=Q, zeta_ld=zeta_ld, n=len(ap))

t, a = make_ringdown(noise=0.01)                   # «дзвін» із ζ=0.05, f_d=45 Гц, шум 1%
r = estimate_damping(t, a)
print(f"частота дзвону  f_d = {r['f_d']:.2f} Гц")
print(f"темп загасання  γ   = {r['gamma']:.2f} 1/с")
print(f"власна частота  ω₀  = {r['w0']:.1f} рад/с")
print(f"ζ (обвідна)         = {r['zeta']:.4f}")
print(f"ζ (лог-декремент)   = {r['zeta_ld']:.4f}")
print(f"добротність     Q   = {r['Q']:.1f}   (по {r['n']} вершинах)")
