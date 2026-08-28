g = np.array([0.0, -9.8])                     # тяжіння вниз

def linear_drag(m, k):                        # опір ∝ швидкості (мале, повільне тіло)
    return lambda r, v: g - (k / m) * v

def quadratic_drag(m, c):                     # опір ∝ швидкості² (реальне повітря)
    return lambda r, v: g - (c / m) * np.linalg.norm(v) * v

def simulate(accel, r0, v0, dt, steps, step=euler):
    r, v = np.array(r0, float), np.array(v0, float)
    R = np.empty((steps + 1, 2)); R[0] = r
    V = np.empty_like(R);         V[0] = v
    for i in range(steps):                    # ← гарячий цикл: тут живе вся вартість
        r, v = step(r, v, accel, dt)
        R[i + 1], V[i + 1] = r, v
    return np.arange(steps + 1) * dt, R, V
