import math

def simulate_oxram_cell(v_max=2.0, steps=400, i_comp=1e-4):
    """
    Моделювання вольт-амперного гістерезису та кінетики зазору OxRAM комірки.
    """
    # Фізичні константи
    q = 1.602e-19
    kB = 1.38e-23
    L_W = 2.44e-8
    
    # Параметри комірки HfO2
    x_gap = 1.2e-9        # Початковий зазор HRS (м)
    E_a = 0.85 * 1.602e-19 # Енергія активації (Дж)
    a = 0.3e-9            # Відстань між ямами (м)
    v0 = 1e4              # Пре-експоненційний множник (м/с)
    R_on = 1000.0         # Опір LRS філамента (Ом)
    T0 = 300.0            # Базова температура (К)
    dt = 1e-6             # Крок за часом (с)

    # Генерація трикутного імпульсу напруги (0 -> V_max -> 0 -> -V_max -> 0)
    v_profile = []
    half = steps // 4
    for i in range(half):
        v_profile.append((i / half) * v_max)
    for i in range(half):
        v_profile.append((1.0 - i / half) * v_max)
    for i in range(half):
        v_profile.append(-(i / half) * v_max)
    for i in range(half):
        v_profile.append(-(1.0 - i / half) * v_max)

    history_v = []
    history_i = []
    history_gap = []

    for V_app in v_profile:
        # Опір тунельного зазору R_gap = R_on * exp(A * x_gap)
        R_gap = R_on * math.exp(10.25e9 * x_gap)
        R_total = R_on + R_gap

        # Розрахунок струму з урахуванням обмеження I_comp
        I_cell = V_app / R_total
        if abs(I_cell) > i_comp:
            I_cell = math.copysign(i_comp, I_cell)

        # Падіння напруги безпосередньо на зазорі
        V_gap = I_cell * R_gap
        E_gap = abs(V_gap) / max(x_gap, 1e-10)

        # Температура за співвідношенням Кольрауша
        T_max = math.sqrt(T0**2 + (abs(V_gap)**2) / (4.0 * L_W))

        # Швидкість руху вакансій за Моттом — Ґерні
        arg = (q * a * E_gap) / (2.0 * kB * T_max)
        arg = min(arg, 50.0) # Захист від переповнення exp
        v_drift = 2.0 * a * v0 * math.exp(-E_a / (kB * T_max)) * math.sinh(arg)

        # Зміна зазору залежно від полярності (SET при V > 0, RESET при V < 0)
        if V_app > 0:
            dx_dt = -v_drift # Звуження зазору
        else:
            dx_dt = v_drift * 0.1 # Розширення зазору при RESET

        x_gap = max(0.0, min(2.0e-9, x_gap + dx_dt * dt))

        history_v.append(V_app)
        history_i.append(I_cell)
        history_gap.append(x_gap)

    return history_v, history_i, history_gap

if __name__ == "__main__":
    v_arr, i_arr, gap_arr = simulate_oxram_cell()
    print(f"Моделювання завершено. Завершальний зазор x_gap: {gap_arr[-1]*1e9:.3f} нм")
