import numpy as np

def simulate_dipole_rotation(p_val, E_val, I_val, gamma_val, theta0_deg=90.0, t_max_ps=5.0):
    """
    Моделювання обертальної динаміки диполя в однорідному полі методом RK4.
    """
    theta0 = np.radians(theta0_deg)
    state = np.array([theta0, 0.0]) # [theta, omega]
    dt = 1e-14 # 10 фс
    steps = int(t_max_ps * 1e-12 / dt)

    times = np.linspace(0, t_max_ps, steps)
    angles = np.zeros(steps)

    def rhs(st):
        th, om = st[0], st[1]
        dth = om
        dom = (-p_val * E_val * np.sin(th) - gamma_val * om) / I_val
        return np.array([dth, dom])

    for i in range(steps):
        angles[i] = np.degrees(state[0])
        # Крок RK4
        k1 = rhs(state)
        k2 = rhs(state + 0.5 * dt * k1)
        k3 = rhs(state + 0.5 * dt * k2)
        k4 = rhs(state + dt * k3)
        state += (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

    return times, angles

if __name__ == "__main__":
    p_h2o = 1.85 * 3.33564e-30
    E_ext = 1e6
    I_h2o = 2.0e-47
    gamma = 1.0e-36

    t, deg = simulate_dipole_rotation(p_h2o, E_ext, I_h2o, gamma)
    print(f"Симуляцію завершено. Кінцевий кут диполя: {deg[-1]:.2f}° (орієнтація за полем).")
