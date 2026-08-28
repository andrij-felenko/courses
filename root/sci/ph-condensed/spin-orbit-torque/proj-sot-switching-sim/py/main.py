import math
import numpy as np

def simulate_sot_switching():
    # Фізичні константи
    hbar = 1.054571817e-34      # Дж·с
    e_charge = 1.602176634e-19  # Кл
    mu0 = 4.0 * math.pi * 1e-7  # Гн/м
    gamma_bar = 1.7608596e11    # Рад/(с·Тл)
    gamma_mu0 = gamma_bar * mu0

    # Параметри гетероструктури SOT
    Ms = 1.0e6            # Намагніченість насичення (А/м)
    Hk_eff = 4.0e5        # Ефективне поле анізотропії PMA (А/м)
    Bx = 0.05             # Допоміжне поле B_x (Тл)
    alpha = 0.02          # Загасання Гільберта
    theta_SH = 0.30       # Кут спинового Холла (β-W)
    d_fm = 1.2e-9         # Товщина шару CoFeB (м)
    Jc = 1.2e11           # Густина струму (А/м²)

    # Параметри часу
    dt = 1.0e-13          # Крок часової сітки (0.1 пс)
    t_pulse = 1.0e-9      # Тривалість струму (1 нс)
    t_total = 2.0e-9      # Загальний час моделювання (2 нс)
    steps = int(t_total / dt)

    # Орт спинової поляризації σ = (0, 1, 0)
    sigma = np.array([0.0, 1.0, 0.0])

    def compute_dmdt(m_vec, current_active):
        # 1. Внутрішнє ефективне поле
        Heff = np.array([Bx / mu0, 0.0, Hk_eff * m_vec[2]])

        # 2. Амплитуда Damping-like поля
        H_DL = (hbar * theta_SH * Jc) / (2.0 * e_charge * Ms * d_fm) if current_active else 0.0

        # 3. Векторні добутки
        m_cross_Heff = np.cross(m_vec, Heff)
        m_cross_m_cross_Heff = np.cross(m_vec, m_cross_Heff)

        m_cross_sigma = np.cross(m_vec, sigma)
        m_cross_m_cross_sigma = np.cross(m_vec, m_cross_sigma)

        # 4. Рівняння LLGS
        factor = 1.0 / (1.0 + alpha**2)
        precession = -gamma_mu0 * m_cross_Heff
        damping = -gamma_mu0 * alpha * m_cross_m_cross_Heff
        sot_dl = gamma_mu0 * H_DL * m_cross_m_cross_sigma
        sot_fl = alpha * gamma_mu0 * H_DL * m_cross_sigma

        return factor * (precession + damping + sot_dl + sot_fl)

    # Початковий стан m_z ≈ +1
    m = np.array([0.05, 0.0, 0.9987])
    m = m / np.linalg.norm(m)

    print("Час (нс)\t m_x\t\t m_y\t\t m_z")
    print("-" * 55)

    for step in range(steps + 1):
        t = step * dt
        current_active = (t <= t_pulse)

        if step % 2000 == 0:
            print(f"{t * 1e9:.3f} нс\t {m[0]:.4f}\t {m[1]:.4f}\t {m[2]:.4f}")

        # Інтегрування методом Рунге-Кутти 4-го порядку (RK4)
        k1 = compute_dmdt(m, current_active)
        k2 = compute_dmdt(m + 0.5 * dt * k1, current_active)
        k3 = compute_dmdt(m + 0.5 * dt * k2, current_active)
        k4 = compute_dmdt(m + dt * k3, current_active)

        m = m + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        m = m / np.linalg.norm(m)

    print("-" * 55)
    print(f"Фінальний стан m_z: {m[2]:.4f}")

if __name__ == "__main__":
    simulate_sot_switching()
