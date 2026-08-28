import math
import numpy as np

def simulate_macrospin_sllg(d_nm=8.0, temp_k=300.0, dt_s=1e-13, num_steps=5000000):
    """
    Чисельне моделювання термофлуктуацій макроспіна однодоменної частинки методом sLLG (Heun).
    """
    kb = 1.380649e-23
    gamma = 1.76e11
    ms = 1.4e6
    ku = 4.5e5
    alpha = 0.1

    vol = (math.pi / 6.0) * (d_nm * 1e-9)**3
    gamma_prime = gamma / (1.0 + alpha**2)
    hk = 2.0 * ku / ms
    stdev_h_th = math.sqrt((2.0 * alpha * kb * temp_k) / (gamma * ms * vol))

    m = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    flips = 0
    state = 1

    def sllg_rhs(m_vec, h_eff):
        m_x_h = np.cross(m_vec, h_eff)
        m_x_m_x_h = np.cross(m_vec, m_x_h)
        return -gamma_prime * m_x_h - alpha * gamma_prime * m_x_m_x_h

    dt_sqrt = math.sqrt(dt_s)

    for _ in range(num_steps):
        # Поле Ланжевена
        h_th = stdev_h_th * np.random.normal(0.0, 1.0, 3) / dt_sqrt
        h_eff = h_th + np.array([0.0, 0.0, hk * m[2]])

        # Предиктор Хена
        k1 = sllg_rhs(m, h_eff)
        m_pred = m + k1 * dt_s
        m_pred /= np.linalg.norm(m_pred)

        # Коректор Хена
        h_eff_pred = h_th + np.array([0.0, 0.0, hk * m_pred[2]])
        k2 = sllg_rhs(m_pred, h_eff_pred)

        m += 0.5 * (k1 + k2) * dt_s
        m /= np.linalg.norm(m)

        # Фіксація перевертання
        if state == 1 and m[2] < -0.2:
            state = -1
            flips += 1
        elif state == -1 and m[2] > 0.2:
            state = 1
            flips += 1

    tau_th = 1e-9 * math.exp((ku * vol) / (kb * temp_k))
    return num_steps * dt_s, flips, tau_th

if __name__ == "__main__":
    print("=== Моделювання релаксації Нееля — Брауна в Python ===")
    total_t, count, tau_exp = simulate_macrospin_sllg()
    print(f"Час симуляції: {total_t:.2e} с")
    print(f"Кількість спонтанних перевертань: {count}")
    print(f"Теоретичний час релаксації τ: {tau_exp:.2e} с")
