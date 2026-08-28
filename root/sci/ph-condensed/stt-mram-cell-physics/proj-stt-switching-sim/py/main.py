import math

class PMTJSimulator:
    def __init__(self, ms=1.0e6, hk_eff=0.3, alpha=0.01, polarization=0.6, t_fl_nm=1.3):
        # Фізичні константи
        self.hbar = 1.0545718e-34     # Дж·с (зведена стала Планка)
        self.e = 1.6021766e-19        # Кл (заряд електрона)
        self.gamma0 = 2.211e5         # м/(А·с) (гіромагнітне відношення)
        self.mu0 = 1.256637e-6        # Гн/м (магнітна стала)

        # Параметри pMTJ осередку
        self.ms = ms                  # Намагніченість насичення, А/м
        self.hk_eff = hk_eff          # Ефективне поле анізотропії, Тл
        self.alpha = alpha            # Загасання Гільберта
        self.pol = polarization       # Спінова поляризація P
        self.t_fl = t_fl_nm * 1.0e-9  # Товщина вільного шару, м

    def stt_amplitude(self, j_density):
        """Обчислення амплітуди спінового моменту a_J для заданої густини струму J (А/м²)."""
        return (self.hbar * j_density * self.pol) / (2.0 * self.e * self.ms * self.t_fl)

    def cross(self, a, b):
        """Векторний добуток двох тривимірних векторів."""
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        )

    def compute_dmdt(self, m, j_density):
        """Розрахунок правої частини рівняння LLGS: dm/dt."""
        mx, my, mz = m
        a_j = self.stt_amplitude(j_density)

        # Ефективне поле анізотропії H_eff у напрямку Z (в А/м)
        h_eff = (0.0, 0.0, (self.hk_eff / self.mu0) * mz)
        m_p = (0.0, 0.0, 1.0) # Фіксований шар орієнтований вздовж +Z

        # Векторні добутки
        m_x_h = self.cross(m, h_eff)
        m_x_m_x_h = self.cross(m, m_x_h)

        m_x_mp = self.cross(m, m_p)
        m_x_m_x_mp = self.cross(m, m_x_mp)

        factor = -self.gamma0 / (1.0 + self.alpha**2)

        dm = []
        for i in range(3):
            # Покомпонентне додавання прецесійного, дисипативного та STT членів
            val = (m_x_h[i] + self.alpha * m_x_m_x_h[i] 
                   - a_j * m_x_m_x_mp[i] - self.alpha * a_j * m_x_mp[i])
            dm.append(factor * val)
        return tuple(dm)

    def simulate_pulse(self, j_density, pulse_duration_ns, dt_ps=0.1):
        """Інтегрування рівняння LLGS методом RK4 за час pulse_duration_ns."""
        dt = dt_ps * 1.0e-12
        steps = int((pulse_duration_ns * 1.0e-9) / dt)

        # Початковий стан: шар орієнтований майже в -Z (AP стан) з незначним термічним відхиленням 3°
        theta_init = math.radians(3.0)
        m = (math.sin(theta_init), 0.0, -math.cos(theta_init))

        history_mz = []
        history_mx = []
        for s in range(steps):
            history_mz.append(m[2])
            history_mx.append(m[0])

            # Крок 1 RK4
            k1 = self.compute_dmdt(m, j_density)

            # Крок 2 RK4
            m_k2 = tuple(m[i] + 0.5 * dt * k1[i] for i in range(3))
            k2 = self.compute_dmdt(m_k2, j_density)

            # Крок 3 RK4
            m_k3 = tuple(m[i] + 0.5 * dt * k2[i] for i in range(3))
            k3 = self.compute_dmdt(m_k3, j_density)

            # Крок 4 RK4
            m_k4 = tuple(m[i] + dt * k3[i] for i in range(3))
            k4 = self.compute_dmdt(m_k4, j_density)

            # Оновлення вектора
            m_next = []
            for i in range(3):
                m_next.append(m[i] + (dt / 6.0) * (k1[i] + 2.0*k2[i] + 2.0*k3[i] + k4[i]))

            # Примусове нормування модуля |m| = 1
            norm = math.sqrt(sum(x**2 for x in m_next))
            m = tuple(x / norm for x in m_next)

        return history_mz, history_mx, m[2]

# Демонстраційний запуск
if __name__ == "__main__":
    sim = PMTJSimulator(ms=1.0e6, hk_eff=0.3, alpha=0.01, polarization=0.6, t_fl_nm=1.3)
    j_test = 7.5e10 # 7.5 MA/cm² (вище критичного струму J_c0)
    mz_hist, mx_hist, final_mz = sim.simulate_pulse(j_density=j_test, pulse_duration_ns=3.0)
    print(f"Початкове m_z: -0.9986")
    print(f"Кінцеве m_z після 3 нс імпульсу: {final_mz:.4f}")
    if final_mz > 0.5:
        print("УСПІХ: Намагніченість переключилася в паралельний стан (P)!")
    else:
        print("ПОМИЛКА: Переключення не відбулося.")
