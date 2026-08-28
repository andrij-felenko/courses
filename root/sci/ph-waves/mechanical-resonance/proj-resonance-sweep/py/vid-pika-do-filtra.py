def notch_coeffs(f0, fs, Q):
    """Коефіцієнти цифрового режекторного біквада (RBJ cookbook), нормовані a0=1.
    f0 — центр (Гц); fs — частота дискретизації (Гц); Q — гострота (ширина ≈ f0/Q)."""
    w0    = 2*np.pi * f0 / fs
    alpha = np.sin(w0) / (2*Q)
    cw    = np.cos(w0)
    a0 = 1 + alpha
    b = np.array([1.0,      -2*cw, 1.0])      / a0   # b0, b1, b2
    a = np.array([1 + alpha, -2*cw, 1 - alpha]) / a0 # ділимо ВЕСЬ рядок на a0 → a0 стає 1
    return b, a

b, a = notch_coeffs(f0=63.7, fs=8000.0, Q=6.0)    # гіро дрона: 8 кГц
print("b =", b.round(5))     # [ 0.99585 -1.98921  0.99585]
print("a =", a.round(5))     # [ 1.      -1.98921  0.9917 ]
