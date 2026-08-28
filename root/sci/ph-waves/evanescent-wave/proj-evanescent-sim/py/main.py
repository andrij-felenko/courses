import numpy as np

def simulate_evanescent_wave_and_ftir():
    """
    Чисельна симуляція еванесцентного поля та оптичного тунелювання (FTIR)
    для трьохшарової системи Скло — Повітря — Скло.
    """
    # Параметри оптичної системи
    n1 = 1.52             # Показник заломлення скляної призми (крон)
    n2 = 1.00             # Показник заломлення повітряного зазору
    n3 = 1.52             # Показник заломлення вихідної призми
    wavelength_nm = 632.8 # Довжина хвилі He-Ne лазера (нм)
    theta_deg = 45.0      # Кут падіння (градуси)

    theta_rad = np.radians(theta_deg)
    theta_c_deg = np.degrees(np.arcsin(n2 / n1))

    print(f"Критичний кут ПВВ: theta_c = {theta_c_deg:.2f}°")

    if theta_deg <= theta_c_deg:
        print("Помилка: Заданий кут падіння менший за критичний!")
        return

    # Хвильові числа
    k0 = 2.0 * np.pi / wavelength_nm
    sin_theta = np.sin(theta_rad)
    cos_theta = np.cos(theta_rad)

    # Параметри згасання
    kappa_z = k0 * np.sqrt(n1**2 * sin_theta**2 - n2**2)
    d_p = 1.0 / kappa_z
    d_I = d_p / 2.0

    print(f"Глибина проникнення поля d_p: {d_p:.2f} нм")
    print(f"Глибина згасання інтенсивності d_I: {d_I:.2f} нм\n")

    # 1. Розрахунок просторового розподілу амплітуди по осі z
    z_array = np.linspace(0, 3 * d_p, 7)
    E_rel = np.exp(-z_array / d_p)
    I_rel = E_rel**2

    print("Профіль згасання поля вглиб другого середовища:")
    print(" z (нм) | z / d_p | E(z)/E0 | I(z)/I0")
    for z, E, I in zip(z_array, E_rel, I_rel):
        print(f"{z:7.1f} | {z/d_p:7.2f} | {E:7.4f} | {I:7.4f}")

    # 2. Розрахунок оптичного тунелювання FTIR для s- та p-поляризацій
    gaps_nm = np.linspace(0, 1000, 11)

    # Адмітансні коефіцієнти
    p1_s = n1 * cos_theta
    p2_s = kappa_z / k0
    A_s = ((p1_s**2 + p2_s**2)**2) / (4.0 * p1_s**2 * p2_s**2)

    p1_p = cos_theta / n1
    p2_p = (kappa_z / k0) / (n2**2)
    A_p = ((p1_p**2 + p2_p**2)**2) / (4.0 * p1_p**2 * p2_p**2)

    Ts = 1.0 / (1.0 + A_s * np.sinh(kappa_z * gaps_nm)**2)
    Tp = 1.0 / (1.0 + A_p * np.sinh(kappa_z * gaps_nm)**2)

    # Втрати у децибелах
    loss_db_s = -10.0 * np.log10(np.maximum(Ts, 1e-12))

    print("\nЗалежність тунелювання FTIR T(d) від ширини зазору d:")
    print(" d (нм) | d / lambda0 | T_s (%) | T_p (%) | Втрати (dB)")
    for d, ts_val, tp_val, db_val in zip(gaps_nm, Ts, Tp, loss_db_s):
        print(f"{d:7.1f} | {d / wavelength_nm:10.3f} | {ts_val * 100:6.2f}% | {tp_val * 100:6.2f}% | {db_val:6.2f} dB")

if __name__ == '__main__':
    simulate_evanescent_wave_and_ftir()
