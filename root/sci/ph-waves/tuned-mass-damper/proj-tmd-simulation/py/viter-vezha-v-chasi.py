def sway(mu, f, zeta, zeta_s, dt, n, w, tmd=True):
    k  = mu*f*f  if tmd else 0.0         # tmd=False → гаситель відчеплено (гола вежа)
    c  = 2*zeta*mu if tmd else 0.0
    cs = 2*zeta_s
    def deriv(s, F):
        x1, v1, x2, v2 = s
        return np.array([v1,
                         -x1 - cs*v1 - k*(x1-x2) - c*(v1-v2) + F,   # ẍ₁ (M=1)
                         v2,
                         (-k*(x2-x1) - c*(v2-v1)) / mu])            # ẍ₂ (m=μ)
    s, x = np.zeros(4), np.empty(n)
    for i in range(n):
        F0, F1, Fm = w[i], w[i+1], 0.5*(w[i]+w[i+1])   # сила на початку, кінці й середині кроку
        k1 = deriv(s,            F0)
        k2 = deriv(s + 0.5*dt*k1, Fm)
        k3 = deriv(s + 0.5*dt*k2, Fm)
        k4 = deriv(s + dt*k3,     F1)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4)           # усереднений крок RK4
        x[i] = s[0]
    return x
