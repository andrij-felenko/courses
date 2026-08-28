import math

def simulate_z_pinch(I0=1e5, R0=0.02, rho0=1e-4, T0_ev=2.0, num_steps=2000, dt=5e-10):
    """
    Чисельне моделювання радіального стискання Z-пінчу за моделлю Snowplow.
    
    Параметри:
      I0      : амплітуда струму розряду (Ампер)
      R0      : початковий радіус розрядної камери (метр)
      rho0    : початкова густина газу (кг/м³)
      num_steps: кількість кроків за часом
      dt      : крок інтегрування (секунди)
    """
    mu0 = 4.0 * math.pi * 1e-7
    kB = 1.380649e-23
    ev_to_j = 1.60218e-19
    
    # Початкова погонна маса на стінці
    M_initial = math.pi * (R0 ** 2) * rho0
    
    R = R0 * 0.999
    v = 0.0
    omega = 2.0 * math.pi * 1e6  # частота струму 1 МГц
    p0 = 100.0  # початковий газовий тиск (Па)
    
    time_history = []
    radius_history = []
    b_field_history = []
    velocity_history = []
    
    t = 0.0
    for step in range(num_steps):
        # Аксіальний струм імпульсу
        I_t = I0 * math.sin(omega * t) if t < (math.pi / omega) else 0.0
        
        # Погонна маса згребеного газу (модель Snowplow)
        M_L = math.pi * (R0**2 - R**2) * rho0 + 1e-12
        
        # Магнітна сила стискання (на одиницю довжини)
        f_mag = - (mu0 * (I_t ** 2)) / (4.0 * math.pi * R) if R > 1e-6 else 0.0
        
        # Газокінетичний протитиск (адіабата gamma = 5/3)
        p_th = p0 * ((R0 / R) ** (10.0 / 3.0))
        f_th = 2.0 * math.pi * R * p_th
        
        # Сумарне прискорення плазмової оболонки
        accel = (f_mag + f_th) / M_L
        
        # Інтегрування Симплектичним методом Ейлера
        v += accel * dt
        R += v * dt
        
        # Обмеження кумуляції на осі (фізичний відскок від ядра)
        if R < 0.005 * R0:
            R = 0.005 * R0
            v = - 0.4 * v  # дисипативний відскок
            
        B_surface = (mu0 * abs(I_t)) / (2.0 * math.pi * R) if R > 1e-6 else 0.0
        
        t += dt
        time_history.append(t * 1e6)        # мкс
        radius_history.append(R * 1e3)      # мм
        velocity_history.append(v * 1e-3)   # км/с
        b_field_history.append(B_surface)   # Тл
        
    return time_history, radius_history, velocity_history, b_field_history

def compute_bennett_profiles(r_max=0.01, num_pts=200, a=0.002, I_total=1e5):
    """
    Обчислення радіальних профілів стаціонарної рівноваги Беннетта.
    """
    mu0 = 4.0 * math.pi * 1e-7
    dr = r_max / num_pts
    
    results = []
    for i in range(num_pts):
        r = i * dr
        # Відносна концентрація n(r) / n0
        n_rel = 1.0 / ((1.0 + (r / a)**2) ** 2)
        # Відносна густина струму j_z(r) / j0
        j_rel = n_rel
        # Магнітне поле B_phi(r)
        B_phi = (mu0 * I_total / (2.0 * math.pi)) * (r / (r**2 + a**2))
        
        results.append({
            'r_mm': r * 1e3,
            'n_rel': n_rel,
            'j_rel': j_rel,
            'B_T': B_phi
        })
        
    return results

if __name__ == '__main__':
    t_hist, r_hist, v_hist, b_hist = simulate_z_pinch()
    min_r = min(r_hist)
    max_v = max(abs(v) for v in v_hist)
    max_b = max(b_hist)
    
    print(f"=== ЗВІТ МОДЕЛЮВАННЯ Z-ПІНЧУ ===")
    print(f"Мінімальний радіус кумуляції : {min_r:.3f} мм")
    print(f"Максимальна швидкість поршня : {max_v:.2f} км/с")
    print(f"Максимальне магнітне поле   : {max_b:.2f} Тл")
    
    bennett_data = compute_bennett_profiles()
    print(f"Обчислено {len(bennett_data)} точок стаціонарного профілю Беннетта.")
