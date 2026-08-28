import math

# Тепловий потенціал k*T/q при заданій абсолютній температурі (К), у вольтах.
def thermal_voltage(T_kelvin):
    k = 1.380649e-23   # стала Больцмана, Дж/К
    q = 1.602177e-19   # заряд електрона, Кл
    return k * T_kelvin / q   # U_T = k*T/q

# PTAT-струм ΔU_BE-джерела: I = U_T*ln(N)/R.
# N — відношення площ переходів, R — резистор у емітері (Ом).
def ptat_current(T_kelvin, N, R_ohm):
    u_t = thermal_voltage(T_kelvin)
    return u_t * math.log(N) / R_ohm   # ∝ T, бо U_T ∝ T

# ptat_current(300.0, 8.0, 5400.0) -> ~9.96 мкА при 300 K (27 °C)
# ptat_current(398.0, 8.0, 5400.0) -> ~13.2 мкА при 398 K (125 °C)
