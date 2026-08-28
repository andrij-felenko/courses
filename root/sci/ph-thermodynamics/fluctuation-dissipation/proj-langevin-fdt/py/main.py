import numpy as np

def simulate_langevin_fdt(m=1.0, k=10.0, gamma=0.5, T=300.0, dt=0.001, n_steps=300000):
    """
    Чисельне інтегрування рівняння Ланжевена та спектральна перевірка ТФД.
    Для наочності використовуємо умовні фізичні одиниці (kB = 1.0).
    """
    kB = 1.0
    sigma = np.sqrt(2.0 * gamma * kB * T / dt)
    
    x = np.zeros(n_steps)
    v = np.zeros(n_steps)
    
    # Інтегрування за схемою Ейлера-Маруями
    for i in range(1, n_steps):
        xi = np.random.normal(0.0, sigma)
        a = (-gamma * v[i-1] - k * x[i-1] + xi) / m
        v[i] = v[i-1] + a * dt
        x[i] = x[i-1] + v[i] * dt

    # Відкидаємо перші 10% точок для термалізації системи
    start_idx = int(n_steps * 0.1)
    x_eq = x[start_idx:]
    v_eq = v[start_idx:]
    N = len(x_eq)
    
    # Розрахунок спектральної густини потужності через FFT
    fft_x = np.fft.rfft(x_eq - np.mean(x_eq))
    Sx_sim = (2.0 * dt / N) * np.abs(fft_x)**2
    freqs = np.fft.rfftfreq(N, d=dt)
    omegas = 2.0 * np.pi * freqs
    
    # Теоретична ТФД-крива Каллена-Велтона
    Sx_theory = (2.0 * kB * T * gamma) / ((k - m * omegas**2)**2 + (gamma * omegas)**2)
    
    # Перевірка теореми рівнорозподілу енергії: <m v^2 / 2> = kB T / 2
    mean_e_kin = 0.5 * m * np.mean(v_eq**2)
    expected_e_kin = 0.5 * kB * T
    
    print("=== Результати чисельного експерименту Ланжевена (Python) ===")
    print(f"Очікувана середня кінетична енергія <E_kin>: {expected_e_kin:.4f}")
    print(f"Отримана середня кінетична енергія <E_kin>:  {mean_e_kin:.4f}")
    print(f"Відносна помилка термалізації:              {abs(mean_e_kin - expected_e_kin)/expected_e_kin*100:.2f}%")
    
    return omegas, Sx_sim, Sx_theory

if __name__ == "__main__":
    omegas, Sx_sim, Sx_theory = simulate_langevin_fdt()
