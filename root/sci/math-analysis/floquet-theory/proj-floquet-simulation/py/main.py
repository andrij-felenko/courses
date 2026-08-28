import numpy as np

def mathieu_matrix(t, a, q):
    """
    Повертає матрицю коефіцієнтів A(t) для рівняння Матьє:
    y'' + (a - 2*q*cos(2*t))*y = 0
    У формі системи 1-го порядку для вектора x = [y, dy/dt]^T:
    dx1/dt = x2
    dx2/dt = -(a - 2*q*cos(2*t)) * x1
    """
    f_t = a - 2.0 * q * np.cos(2.0 * t)
    return np.array([
        [0.0, 1.0],
        [-f_t, 0.0]
    ], dtype=np.float64)

def compute_monodromy_matrix(a, q, period=np.pi, steps=1000):
    """
    Чисельно інтегрує dPhi/dt = A(t)*Phi(t) від t=0 до t=period з Phi(0) = Eye(2).
    Використовує метод Рунге-Кутти 4-го порядку (RK4).
    Повертає матрицю монодромії M = Phi(period).
    """
    dt = period / steps
    phi = np.eye(2, dtype=np.float64)
    t = 0.0

    for _ in range(steps):
        # Етапи Рунге-Кутти 4-го порядку для матричного рівняння
        A1 = mathieu_matrix(t, a, q)
        k1 = A1 @ phi

        A2 = mathieu_matrix(t + 0.5 * dt, a, q)
        k2 = A2 @ (phi + 0.5 * dt * k1)

        k3 = A2 @ (phi + 0.5 * dt * k2)

        A4 = mathieu_matrix(t + dt, a, q)
        k4 = A4 @ (phi + dt * k3)

        phi = phi + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        t += dt

    return phi

def analyze_floquet_stability(a, q, period=np.pi, steps=1000):
    """
    Обчислює мультиплікатори та показники Флоке для заданих параметрів (a, q).
    Повертає словник із результатами аналізу.
    """
    M = compute_monodromy_matrix(a, q, period=period, steps=steps)

    # Власні значення матриці монодромії (мультиплікатори Флоке)
    multipliers = np.linalg.eigvals(M)

    # Показники Флоке: mu = (1/T) * ln(lambda)
    exponents = np.log(multipliers + 0j) / period

    # Максимальний модуль мультиплікатора
    max_modulus = np.max(np.abs(multipliers))

    # Слід матриці монодромії
    trace_M = np.trace(M)

    # Стійкість для консервативної 2D системи: |tr M| <= 2 (з урахуванням похибки)
    is_stable = np.abs(trace_M) <= 2.0 + 1e-5

    return {
        "monodromy_matrix": M,
        "multipliers": multipliers,
        "exponents": exponents,
        "max_modulus": max_modulus,
        "trace": trace_M,
        "is_stable": is_stable
    }

def simulate_trajectory(a, q, period=np.pi, num_periods=5, initial_state=None, steps_per_period=200):
    """
    Інтегрує фазову траєкторію x(t) = [y(t), dy/dt] на декількох періодах для візуалізації.
    """
    if initial_state is None:
        initial_state = np.array([1.0, 0.0], dtype=np.float64)

    total_steps = num_periods * steps_per_period
    dt = period / steps_per_period

    t_arr = np.linspace(0.0, num_periods * period, total_steps + 1)
    x_arr = np.zeros((total_steps + 1, 2), dtype=np.float64)
    x_arr[0] = initial_state

    x_curr = initial_state.copy()
    t_curr = 0.0

    for i in range(total_steps):
        A1 = mathieu_matrix(t_curr, a, q)
        k1 = A1 @ x_curr

        A2 = mathieu_matrix(t_curr + 0.5 * dt, a, q)
        k2 = A2 @ (x_curr + 0.5 * dt * k1)

        k3 = A2 @ (x_curr + 0.5 * dt * k2)

        A4 = mathieu_matrix(t_curr + dt, a, q)
        k4 = A4 @ (x_curr + dt * k3)

        x_curr = x_curr + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        t_curr += dt
        x_arr[i + 1] = x_curr

    return t_arr, x_arr

def scan_stability_map(a_range, q_range, period=np.pi, steps=500):
    """
    Сканує двовимірну сітку параметрів (a, q) та будує бінарну матрицю стійкості.
    """
    na = len(a_range)
    nq = len(q_range)
    grid = np.zeros((na, nq), dtype=bool)

    for i, a in enumerate(a_range):
        for j, q in enumerate(q_range):
            res = analyze_floquet_stability(a, q, period=period, steps=steps)
            grid[i, j] = res["is_stable"]

    return grid

if __name__ == "__main__":
    print("=== АНАЛІЗ ФЛОКЕ ДЛЯ РІВНЯННЯ МАТЬЄ ===")

    # Тестовий виклик у стійкій зоні (a = 1.5, q = 0.2)
    res_stable = analyze_floquet_stability(a=1.5, q=0.2)
    print("\n1. Стійкий режим (a=1.5, q=0.2):")
    print(f"   Матриця монодромії M:\n{res_stable['monodromy_matrix']}")
    print(f"   Слід tr(M): {res_stable['trace']:.6f}")
    print(f"   Мультиплікатори lambda: {res_stable['multipliers']}")
    print(f"   Модулі |lambda|: {np.abs(res_stable['multipliers'])}")
    print(f"   Стійкий: {res_stable['is_stable']}")

    # Тестовий виклик у нестійкій зоні параметричного резонансу (a = 1.0, q = 0.5)
    res_unstable = analyze_floquet_stability(a=1.0, q=0.5)
    print("\n2. Нестійкий режим параметричного резонансу (a=1.0, q=0.5):")
    print(f"   Матриця монодромії M:\n{res_unstable['monodromy_matrix']}")
    print(f"   Слід tr(M): {res_unstable['trace']:.6f}")
    print(f"   Мультиплікатори lambda: {res_unstable['multipliers']}")
    print(f"   Модулі |lambda|: {np.abs(res_unstable['multipliers'])}")
    print(f"   Стійкий: {res_unstable['is_stable']}")
