import sys
import math

# Налаштування виводу юнікоду для системних терміналів
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Фізико-хімічні константи синтезу кварцу ───────────────────────────────────
R_GAS = 8.314          # Універсальна газова стала, Дж/(моль·К)
RHO_QUARTZ = 2650.0     # Густина монокристалічного кварцу, кг/м³
MOLAR_MASS_SIO2 = 0.06008 # Молярна маса SiO2, кг/моль

def calculate_fluid_density(p_mpa: float, t_celsius: float) -> float:
    """Приблизний розрахунок густини надкритичного водного флюїду (г/см³)
    за тиском (МПа) та температурою (°C).
    """
    t_k = t_celsius + 273.15
    # Лінеаризована модель для 0.5–1.0 M розчинів Na2CO3
    rho_base = 1.0 - 0.00075 * (t_celsius - 100.0)
    rho_fluid = rho_base + 0.0022 * (p_mpa - 10.0)
    return max(0.4, min(1.1, rho_fluid))

def calculate_solubility_wt_pct(t_celsius: float, rho_fluid: float) -> float:
    """Обчислення термодинамічної розчинності SiO2 (у масових відсотках, wt%)
    за рівнянням Ван т Гоффа з урахуванням густини флюїду.
    """
    t_k = t_celsius + 273.15
    dh_diss = 28500.0  # Ентальпія розчинення SiO2 у 0.8M Na2CO3, Дж/моль
    
    a_const = 6.2
    b_const = 2.0
    
    ln_s = a_const + b_const * math.log(rho_fluid) - (dh_diss / (R_GAS * t_k))
    solubility = math.exp(ln_s)
    return solubility

def simulate_hydrothermal_growth(
    t_diss_c: float = 390.0,
    t_grow_c: float = 350.0,
    pressure_mpa: float = 120.0,
    baffle_open_pct: float = 4.0,
    growth_days: int = 60
):
    """Моделювання тривалого циклу вирощування кварцу в автоклаві.
    
    Параметри:
      t_diss_c        : температура в зоні розчинення (°C)
      t_grow_c        : температура в зоні росту затравок (°C)
      pressure_mpa    : робочий тиск (МПа)
      baffle_open_pct : перфорація бафла (%)
      growth_days     : тривалість циклу росту (діб)
    """
    delta_t = t_diss_c - t_grow_c
    if delta_t <= 0:
        raise ValueError("Температура розчинення мусить бути вищою за температуру росту!")

    # 1. Густина флюїду та розчинність у двох зонах
    rho_diss = calculate_fluid_density(pressure_mpa, t_diss_c)
    rho_grow = calculate_fluid_density(pressure_mpa, t_grow_c)
    
    s_diss = calculate_solubility_wt_pct(t_diss_c, rho_diss)
    s_grow = calculate_solubility_wt_pct(t_grow_c, rho_grow)
    
    # 2. Абсолютна пересиченість розчину (г/см³ або кг/м³)
    delta_c_wt = s_diss - s_grow
    delta_c_kg_m3 = (delta_c_wt / 100.0) * (rho_grow * 1000.0)

    # 3. Коефіцієнт масопереносу через перфорацію бафла
    k_m_base = 1.2e-6  # м/с
    k_m = k_m_base * (baffle_open_pct / 5.0) * math.sqrt(delta_t / 40.0)

    # 4. Швидкість росту грані Z [0001] (мм/добу)
    mass_flux = k_m * delta_c_kg_m3  # кг/(м²·с)
    v_growth_m_s = mass_flux / RHO_QUARTZ
    v_growth_mm_day = v_growth_m_s * 1000.0 * 86400.0

    # 5. Оцінка дефектоутворення та оптичного поглинання -OH (альфа 3585 см^-1)
    alpha_3585 = 0.05 + 0.45 * math.pow(v_growth_mm_day / 0.8, 1.8)
    
    # Акустична добротність Q-фактора п'єзорезонаторів
    q_factor = 1.35e6 / alpha_3585

    # 6. Динаміка росту товщини кристала по днях
    total_thickness_mm = 0.0
    history = []

    for day in range(1, growth_days + 1):
        # Невелика релаксація шихти з часом (зменшення s_diss на 5% до кінця циклу)
        decay = 1.0 - 0.05 * (day / growth_days)
        daily_growth_mm = v_growth_mm_day * decay
        total_thickness_mm += daily_growth_mm
        
        if day == 1 or day % 10 == 0 or day == growth_days:
            history.append((day, daily_growth_mm, total_thickness_mm))

    # Вивід результатів розрахунку
    print("=" * 65)
    print("      РЕЗУЛЬТАТИ МОДЕЛЮВАННЯ ГІДРОТЕРМАЛЬНОГО СИНТЕЗУ КВАРЦУ")
    print("=" * 65)
    print(f"Температура розчинення (T_diss):    {t_diss_c:.1f} °C")
    print(f"Температура кристалізації (T_grow):  {t_grow_c:.1f} °C (dT = {delta_t:.1f} °C)")
    print(f"Робочий тиск (P):                  {pressure_mpa:.1f} МПа")
    print(f"Перфорація бафла:                  {baffle_open_pct:.1f} %")
    print("-" * 65)
    print(f"Густина флюїду в зоні росту:        {rho_grow:.3f} г/см³")
    print(f"Розчинність в зоні шихти (S_diss): {s_diss:.3f} wt%")
    print(f"Розчинність в зоні росту (S_grow): {s_grow:.3f} wt%")
    print(f"Пересиченість розчину (dC):         {delta_c_wt:.3f} wt% ({delta_c_kg_m3:.2f} кг/м³)")
    print("-" * 65)
    print(f"Швидкість росту Z-грані (v_Z):      {v_growth_mm_day:.3f} мм/добу")
    print(f"Коефіцієнт -OH поглинання (α3585): {alpha_3585:.3f} см⁻¹")
    print(f"Прогнозована добротність Q-фактор:  {q_factor:.2e}")
    print("=" * 65)
    print("\nДинаміка наращування кристала за часом:")
    print(f"{'День':^8}|{'Приріст (мм/добу)':^22}|{'Сумарна товщина (мм)':^24}")
    print("-" * 56)
    for day, d_growth, total_t in history:
        print(f"{day:^8d}|{d_growth:^22.3f}|{total_t:^24.2f}")
    print("-" * 56)

if __name__ == "__main__":
    # Запуск розрахунку для типового промислового режиму
    simulate_hydrothermal_growth(
        t_diss_c=395.0,
        t_grow_c=355.0,
        pressure_mpa=130.0,
        baffle_open_pct=4.5,
        growth_days=60
    )
