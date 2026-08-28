import math

# Частота RHP-нуля бусту в CCM. Vin, Vout — вольти; Iout — ампери; L — генрі.
def rhpz_boost_hz(Vin, Vout, Iout, L):
    D = 1.0 - Vin / Vout                   # шпаруватість
    R = Vout / Iout                        # опір навантаження
    k = (1.0 - D) ** 2                     # (1 − D)²
    return R * k / (2.0 * math.pi * L)

# Смугу контуру безпечно тримати ~у 4 рази нижче за нуль.
def loop_bw_limit_hz(f_rhpz):
    return f_rhpz / 4.0

# приклад: 5 В → 12 В, 1 А, 22 мкГн
# f_rhpz ≈ 15.1 кГц  →  стеля смуги ≈ 3.8 кГц
