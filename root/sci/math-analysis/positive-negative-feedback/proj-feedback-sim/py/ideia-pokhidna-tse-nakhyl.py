import numpy as np

def integrate(f, x0, dt, T, method="rk4"):
    """Проінтегрувати dx/dt = f(x, t) від 0 до T кроком dt.
    x0 — число АБО numpy-вектор стану. Повертає (t, історія-x)."""
    n = int(round(T / dt))
    t = np.linspace(0.0, n * dt, n + 1)
    x = np.empty((n + 1,) + np.shape(x0))
    x[0] = x0
    for i in range(n):
        xi, ti = x[i], t[i]
        if method == "euler":                       # один крок уздовж нахилу
            x[i + 1] = xi + dt * f(xi, ti)
        else:                                       # RK4: чотири проби нахилу
            k1 = f(xi,              ti)
            k2 = f(xi + 0.5*dt*k1,  ti + 0.5*dt)
            k3 = f(xi + 0.5*dt*k2,  ti + 0.5*dt)
            k4 = f(xi + dt*k3,      ti + dt)
            x[i + 1] = xi + dt/6.0 * (k1 + 2*k2 + 2*k3 + k4)
    return t, x
