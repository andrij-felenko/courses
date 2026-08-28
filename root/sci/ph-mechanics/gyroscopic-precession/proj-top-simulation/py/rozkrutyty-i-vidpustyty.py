def spin_up(theta0, w3, phid0=0.0):
    """Стан на старті: нахил θ₀, спін w3 (рад/с), заданий темп прецесії φ̇₀."""
    p_psi = I3 * w3
    p_phi = I1 * phid0 * np.sin(theta0)**2 + p_psi * np.cos(theta0)
    return np.array([theta0, 0.0, 0.0, 0.0, p_phi, p_psi])   # θ̇ = 0: без початкового кивка

dt = 1e-3
y  = spin_up(np.radians(90.0), w3=20.0)     # вісь горизонтально, спін 20 рад/с
theta, phi = [], []
for _ in range(15000):                       # 15 секунд по 1 мс
    y = rk4(y, dt)
    theta.append(y[0]); phi.append(y[1])
theta, phi = np.array(theta), np.array(phi)
