import math
import numpy as np

class MonopoleSimulator:
    """
    Симулятор руху зарядженої частинки у полі магнітного монополя.
    Математичні параметри:
      m: маса частинки (кг або умовні одиниці)
      q: електричний заряд частинки (Кл або умовні одиниці)
      g: магнітний заряд монополя (Вб або умовні одиниці)
    """
    def __init__(self, m: float, q: float, g: float):
        self.m = m
        self.q = q
        self.g = g
        # Константа магнітної взаємодії mu = (q * g) / (4 * pi)
        self.mu = (q * g) / (4.0 * math.pi)

    def accel(self, r: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Обчислення вектора прискорення a = (mu / (m * r^3)) * (v x r)"""
        r_norm = np.linalg.norm(r)
        if r_norm < 1e-12:
            return np.zeros(3)
        cross_vr = np.cross(v, r)
        return (self.mu / (self.m * (r_norm**3))) * cross_vr

    def poincare_vector(self, r: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Обчислення вектора Пуанкаре J = m * (r x v) - mu * r_hat"""
        r_norm = np.linalg.norm(r)
        if r_norm < 1e-12:
            return np.zeros(3)
        r_hat = r / r_norm
        L = self.m * np.cross(r, v)
        return L - self.mu * r_hat

    def step_rk4(self, r: np.ndarray, v: np.ndarray, dt: float):
        """Один крок чисельного інтегрування методом RK4"""
        k1_r = v
        k1_v = self.accel(r, v)

        r2 = r + 0.5 * dt * k1_r
        v2 = v + 0.5 * dt * k1_v
        k2_r = v2
        k2_v = self.accel(r2, v2)

        r3 = r + 0.5 * dt * k2_r
        v3 = v + 0.5 * dt * k2_v
        k3_r = v3
        k3_v = self.accel(r3, v3)

        r4 = r + dt * k3_r
        v4 = v + dt * k3_v
        k4_r = v4
        k4_v = self.accel(r4, v4)

        r_next = r + (dt / 6.0) * (k1_r + 2.0 * k2_r + 2.0 * k3_r + k4_r)
        v_next = v + (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
        return r_next, v_next

def main():
    # Налаштування моделі: m=1.0, q=1.0, g=4*pi (mu=1.0)
    sim = MonopoleSimulator(m=1.0, q=1.0, g=4.0 * math.pi)

    # Початкові умови: r0 = (-5.0, 1.0, 0.0), v0 = (1.0, 0.0, 0.0)
    r = np.array([-5.0, 1.0, 0.0])
    v = np.array([1.0, 0.0, 0.0])
    dt = 0.001
    steps = 10000

    J0 = sim.poincare_vector(r, v)
    E0 = 0.5 * sim.m * np.dot(v, v)
    cos_theta = -sim.mu / np.linalg.norm(J0)
    theta_deg = math.degrees(math.acos(cos_theta))

    print(f"Початкова кінетична енергія E0 = {E0:.6f}")
    print(f"Вектор Пуанкаре J0 = [{J0[0]:.4f}, {J0[1]:.4f}, {J0[2]:.4f}]")
    print(f"Кут напіврозкриття конуса Пуанкаре theta = {theta_deg:.2f} градусів")

    # Інтегрування траєкторії
    for step in range(steps):
        r, v = sim.step_rk4(r, v, dt)

    E_end = 0.5 * sim.m * np.dot(v, v)
    J_end = sim.poincare_vector(r, v)

    print("\n--- Результати після 10000 кроків ---")
    print(f"Кінцева позиція r = [{r[0]:.4f}, {r[1]:.4f}, {r[2]:.4f}]")
    print(f"Кінцева енергія E_end = {E_end:.6f} (абс. помилка: {abs(E_end - E0):.2e})")
    print(f"Похибка вектора Пуанкаре |J_end - J0| = {np.linalg.norm(J_end - J0):.2e}")

if __name__ == "__main__":
    main()
