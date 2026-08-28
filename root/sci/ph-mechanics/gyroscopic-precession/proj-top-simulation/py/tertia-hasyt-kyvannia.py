def run(theta0, w3, T, dt=1e-3, c_th=0.0):
    y = spin_up(np.radians(theta0), w3)
    out = []
    for _ in range(int(T/dt)):
        y = rk4(y, dt, c_th=c_th)
        out.append(y[0])                     # записуємо нахил θ
    return np.degrees(out)

th_free = run(90.0, 20.0, 8.0, c_th=0.0)     # без тертя
th_damp = run(90.0, 20.0, 8.0, c_th=0.30)    # з тертям
