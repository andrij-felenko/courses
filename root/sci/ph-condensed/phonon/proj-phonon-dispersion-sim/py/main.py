import math

def calculate_monoatomic_dispersion(m, c, a, num_points=100):
    """
    Розрахунок акустичної гілки одноатомного ланцюжка.
    
    Параметри:
    m : float -- маса атома у кг
    c : float -- коефіцієнт міжатомної жорсткості у Н/м
    a : float -- стала ґратки у метрах
    num_points : int -- кількість точок розбиття першої зони Бріллюена
    
    Повертає:
    k_vals, w_vals, vg_vals -- масиви хвильових векторів (1/м), частот (рад/с) та групових швидкостей (м/с)
    """
    w_max = 2.0 * math.sqrt(c / m)
    vs_0 = a * math.sqrt(c / m)  # Швидкість звуку при k->0
    
    k_vals = []
    w_vals = []
    vg_vals = []
    
    for i in range(num_points + 1):
        # Хвильовий вектор від 0 до pi/a
        k = (math.pi / a) * (i / num_points)
        w = w_max * math.sin(k * a / 2.0)
        vg = (a / 2.0) * math.sqrt(c / m) * math.cos(k * a / 2.0)
        
        k_vals.append(k)
        w_vals.append(w)
        vg_vals.append(vg)
        
    return k_vals, w_vals, vg_vals, w_max, vs_0

def calculate_diatomic_dispersion(m1, m2, c, a, num_points=100):
    """
    Розрахунок акустичної та оптичної гілок для двоатомного ланцюжка.
    
    Параметри:
    m1, m2 : float -- маси атомів у елементарній комірці (кг)
    c : float -- жорсткість зв'язку (Н/м)
    a : float -- період ґратки (м)
    """
    k_vals = []
    w_ac = []
    w_opt = []
    
    term1 = c * (1.0 / m1 + 1.0 / m2)
    
    for i in range(num_points + 1):
        k = (math.pi / a) * (i / num_points)
        sin_sq = math.sin(k * a / 2.0) ** 2
        
        # Дискримінант під коренем
        radicand = (1.0 / m1 + 1.0 / m2)**2 - (4.0 * sin_sq) / (m1 * m2)
        term2 = c * math.sqrt(max(0.0, radicand))
        
        w_ac_sq = max(0.0, term1 - term2)
        w_opt_sq = term1 + term2
        
        k_vals.append(k)
        w_ac.append(math.sqrt(w_ac_sq))
        w_opt.append(math.sqrt(w_opt_sq))
        
    return k_vals, w_ac, w_opt

def debye_integrand(x):
    """
    Підінтегральна функція f(x) = x^4 * e^x / (e^x - 1)^2
    З урахуванням граничних асимптотик для розривів.
    """
    if x < 1e-5:
        return x * x  # Граничний перехід при x->0
    if x > 80.0:
        return 0.0    # Асимптотичне загасання exp(-x) при великих x
    
    exp_x = math.exp(x)
    return (x ** 4) * exp_x / ((exp_x - 1.0) ** 2)

def debye_heat_capacity(t_ratio, num_steps=2000):
    """
    Чисельне інтегрування методом трапецій для молярної теплоємності C_v / R.
    
    t_ratio : float -- відношення T / Theta_D
    """
    if t_ratio <= 0.0:
        return 0.0
    
    # Захист для дуж низьких температур (кубічний закон)
    if t_ratio < 0.01:
        return (12.0 * (math.pi ** 4) / 5.0) * (t_ratio ** 3)
    
    x_max = 1.0 / t_ratio
    dx = x_max / num_steps
    
    integral_sum = 0.5 * (debye_integrand(0.0) + debye_integrand(x_max))
    for i in range(1, num_steps):
        x = i * dx
        integral_sum += debye_integrand(x)
        
    integral_val = integral_sum * dx
    cv_over_r = 9.0 * (t_ratio ** 3) * integral_val
    return cv_over_r

def main():
    print("=" * 65)
    print(" МОДЕЛЬУВАННЯ ФОНОННИХ СПЕКТРІВ ТА ТЕПЛОЄМНОСТІ КРИСТАЛІВ")
    print("=" * 65)
    
    # 1. Розрахунок для кремнію (Si)
    amu = 1.660539e-27  # а.о.м. у кг
    m_si = 28.0855 * amu
    c_si = 145.0         # Н/м
    a_si = 5.431e-10     # м
    
    k_v, w_v, vg_v, w_m, vs_0 = calculate_monoatomic_dispersion(m_si, c_si, a_si, num_points=10)
    
    print("\n--- 1. ОДНОАТОМНИЙ ЛАНЦЮЖОК КРЕМНІЮ (Si) ---")
    print(f"Маса атома M: {m_si/amu:.2f} а.о.м.")
    print(f"Максимальна частота w_max: {w_m / (2*math.pi*1e12):.3f} ТГц")
    print(f"Швидкість звуку v_s (k->0): {vs_0/1000.0:.2f} км/с")
    print("-" * 55)
    print("  k (1/нм)  |  Частота w (ТГц)  |  Групова швидкість v_g (км/с)")
    print("-" * 55)
    
    for i in range(len(k_v)):
        k_nm = k_v[i] / 1e9
        w_thz = w_v[i] / (2 * math.pi * 1e12)
        vg_kms = vg_v[i] / 1000.0
        print(f"  {k_nm:8.3f}  |  {w_thz:14.3f}  |  {vg_kms:22.3f}")
        
    # 2. Розрахунок для Арсеніду Галію (GaAs)
    m_ga = 69.723 * amu
    m_as = 74.9216 * amu
    c_gaas = 110.0
    a_gaas = 5.653e-10
    
    k_v, w_a, w_o = calculate_diatomic_dispersion(m_ga, m_as, c_gaas, a_gaas, num_points=6)
    
    print("\n--- 2. ДВОАТОМНИЙ ЛАНЦЮЖОК АРСЕНІДУ ГАЛІЮ (GaAs) ---")
    print(f"Маси підґраток: M1(Ga) = {m_ga/amu:.2f} a.o.m., M2(As) = {m_as/amu:.2f} a.o.m.")
    print("-" * 62)
    print("  k (1/нм)  |  Акустична w_A (ТГц) |  Оптична w_O (ТГц) |  Band Gap (ТГц)")
    print("-" * 62)
    
    for i in range(len(k_v)):
        k_nm = k_v[i] / 1e9
        wa_thz = w_a[i] / (2 * math.pi * 1e12)
        wo_thz = w_o[i] / (2 * math.pi * 1e12)
        gap = wo_thz - wa_thz
        print(f"  {k_nm:8.3f}  |  {wa_thz:17.3f} |  {wo_thz:16.3f} |  {gap:12.3f}")
        
    # 3. Температурний хід теплоємності Дебая
    print("\n--- 3. МОЛЯРНА ТЕПЛОЄМНІСТЬ ДЕБАЯ C_v / R ТА C_v (Дж/(моль·К)) ---")
    print(" T / Theta_D | C_v / (3R) | C_v Дж/(моль·К) | Фізичний режим")
    print("-" * 62)
    
    r_gas = 8.31446
    t_ratios = [0.005, 0.01, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 2.0, 5.0]
    for tr in t_ratios:
        cv_over_r = debye_heat_capacity(tr)
        cv_norm = cv_over_r / 3.0  # Нормування на 3R (границя Дюлонга-Пті = 1.0)
        cv_abs = cv_over_r * r_gas
        
        if tr <= 0.05:
            regime = "Закон куба Дебая (T³)"
        elif tr >= 2.0:
            regime = "Класична границя Дюлонга — Пті"
        else:
            regime = "Квантовий перехідний режим"
            
        print(f"  {tr:8.3f}  |  {cv_norm:10.4f} |  {cv_abs:14.3f} | {regime}")

if __name__ == "__main__":
    main()
