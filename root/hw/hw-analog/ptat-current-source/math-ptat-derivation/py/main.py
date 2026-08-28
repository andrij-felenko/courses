import math

# Тепловий потенціал U_T = k*T/q при абсолютній температурі T (К), у вольтах.
def thermal_voltage(T_kelvin):
    k = 1.380649e-23   # стала Больцмана, Дж/К
    q = 1.602177e-19   # елементарний заряд, Кл
    return k * T_kelvin / q

# Різниця падінь база-емітер двох переходів із відношенням площ N.
# ΔU_BE = U_T*ln(N) — чистий PTAT, лінійний крізь нуль.
def delta_vbe(T_kelvin, N):
    return thermal_voltage(T_kelvin) * math.log(N)   # ∝ T

# Нахил d(ΔU_BE)/dT = (k/q)*ln(N) — стала, та сама при будь-якій T.
def delta_vbe_slope(N):
    k_over_q = 8.617333e-5   # В/К
    return k_over_q * math.log(N)                     # ≈ 0.1792 мВ/К для N=8

# delta_vbe(233.15, 8.0) -> ~41.8 мВ   (−40 °C)
# delta_vbe(398.15, 8.0) -> ~71.3 мВ   (+125 °C)
# Перевірка лінійності: (71.3 − 41.8) / (398.15 − 233.15) = 0.1792 мВ/К — той самий нахил.
