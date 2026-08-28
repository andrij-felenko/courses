import math
import numpy as np

def iso9613_alpha(frequency_hz, temp_c=20.0, pressure_kpa=101.325, relative_humidity_pct=50.0):
    """
    Обчислення коефіцієнта атмосферного поглинання за стандартом ISO 9613-1.
    Повертає α у дБ/м та дБ/км.
    """
    p_pr = 101.325
    T_pr = 293.15
    T_01 = 273.16

    T_k = temp_c + 273.15
    p_rel = pressure_kpa / p_pr
    T_rel = T_k / T_pr

    # 1. Молярна концентрація вологи h
    exp_val = -6.8346 * math.pow(T_01 / T_k, 1.261) + 4.6151
    p_sat_rel = math.pow(10.0, exp_val)
    h = relative_humidity_pct * (p_sat_rel / p_rel)

    # 2. Частоти релаксації
    fr_O = p_rel * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h))
    fr_N = p_rel * math.pow(T_rel, -0.5) * (9.0 + 280.0 * h * math.exp(-4.17 * (math.pow(T_rel, -1/3) - 1.0)))

    # 3. Складові поглинання
    f = np.asarray(frequency_hz, dtype=float)
    f2 = f ** 2

    alpha_cl = 1.84e-11 * (1.0 / p_rel) * math.sqrt(T_rel)
    alpha_O = math.pow(T_rel, -2.5) * 0.1068 * math.exp(-3352.0 / T_k) * (fr_O / (fr_O**2 + f2))
    alpha_N = math.pow(T_rel, -2.5) * 0.01275 * math.exp(-2239.1 / T_k) * (fr_N / (fr_N**2 + f2))

    alpha_db_m = 8.686 * f2 * (alpha_cl + alpha_O + alpha_N)
    return alpha_db_m, alpha_db_m * 1000.0

if __name__ == '__main__':
    alpha_m, alpha_km = iso9613_alpha(4000.0, temp_c=20.0, relative_humidity_pct=50.0)
    print(f"ISO 9613-1 (Python): 4 кГц при 20°C, 50% RH = {alpha_km:.2f} дБ/км ({alpha_m:.5f} дБ/м)")
