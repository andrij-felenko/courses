import math
import numpy as np

def simulate_eddy_currents():
    """
    Чисельне моделювання дифузії магнітного поля та вихрових втрат у мідній пластині.
    """
    # Фізичні параметри матеріалу (Мідь)
    sigma = 5.8e7        # Питома провідність (См/м)
    mu_r = 1.0           # Відносна магнітна проникність
    mu_0 = 4.0 * math.pi * 1e-7
    mu = mu_r * mu_0
    
    # Геометрія та поле
    d = 0.002            # Товщина пластини: 2 мм
    f = 1000.0           # Частота поля: 1 кГц
    omega = 2.0 * math.pi * f
    B_0 = 0.1            # Амплітуда індукції: 0.1 Тл
    
    # Розрахунок теоретичної глибини скін-шару
    delta = math.sqrt(2.0 / (omega * mu * sigma))
    print(f"Теоретична глибина скін-шару δ = {delta * 1e3:.4f} мм")
    
    # Дискретизація простору
    N = 101
    dx = d / (N - 1)
    x = np.linspace(-d / 2.0, d / 2.0, N)
    
    # Дифузійність та крок за часом для стійкості CFL
    D_m = 1.0 / (mu * sigma)
    dt = 0.45 * (dx * dx) / D_m
    alpha = D_m * dt / (dx * dx)
    
    # Моделювання 5 повних періодів для виходу на стаціонарний режим
    period = 1.0 / f
    total_time = 5.0 * period
    num_steps = int(total_time / dt)
    
    B = np.zeros(N)
    
    # Інтегрування у часі
    t = 0.0
    for step in range(num_steps):
        t += dt
        B_new = B.copy()
        
        # Внутрішні вузли (Явна різницева схема)
        B_new[1:-1] = B[1:-1] + alpha * (B[2:] - 2.0 * B[1:-1] + B[:-2])
        
        # Граничні умови
        B_ext = B_0 * math.sin(omega * t)
        B_new[0] = B_ext
        B_new[-1] = B_ext
        
        B = B_new
        
    # Розрахунок густини струму j_y = -(1/μ) * (dB/dx) за центральними різницями
    j_y = np.zeros(N)
    j_y[1:-1] = -(1.0 / mu) * (B[2:] - B[:-2]) / (2.0 * dx)
    j_y[0] = -(1.0 / mu) * (B[1] - B[0]) / dx
    j_y[-1] = -(1.0 / mu) * (B[-1] - B[-2]) / dx
    
    # Питома потужність втрат p = j² / σ
    p_e = (j_y ** 2) / sigma
    
    # Об'ємне усереднення втрат за допомогою методу Трапецій
    P_vol_sim = np.trapezoid(p_e, x) / d
    
    # Аналітична оцінка для тонкого листа (d << δ)
    P_vol_analytical = (math.pi ** 2 / 6.0) * sigma * (d ** 2) * (f ** 2) * (B_0 ** 2)
    
    print(f"Чисельні об'ємні втрати P_e:   {P_vol_sim * 1e-3:.2f} кВт/м³")
    print(f"Аналітична оцінка втрат P_e:   {P_vol_analytical * 1e-3:.2f} кВт/м³")

if __name__ == "__main__":
    simulate_eddy_currents()
