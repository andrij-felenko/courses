g, L = 9.8, 1.0                              # нестійкість росте як √(g/L) = 3.13 1/с

def inverted_pendulum(Kp, Kd):
    w2 = g / L
    def f(s, t):
        theta, omega = s
        u = -(Kp*theta + Kd*omega)           # рукотворний від'ємний зв'язок: PD
        return np.array([omega, w2*np.sin(theta) + u])
    return f

s0 = np.array([0.2, 0.0])                    # нахил 0.2 рад ≈ 11°, у спокої
t, s = integrate(inverted_pendulum(Kp=20, Kd=6), s0, dt=0.005, T=10.0)
theta = s[:, 0]                              # → гасне до нуля: балансує
