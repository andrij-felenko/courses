import math

# Розрахунок twin-T режектора під задану частоту-ціль.
# Задаємо ємність бічних конденсаторів C (Ф); повертаємо
# бічний резистор R (Ом). Шунти: R_shunt = R/2, C_shunt = 2*C.
def twint_R_from_f0(f0_hz, c_side_f):
    return 1.0 / (2.0 * math.pi * f0_hz * c_side_f)

# Зворотна перевірка: яка частота провалу вийде на цих R, C.
def twint_f0(r_side_ohm, c_side_f):
    return 1.0 / (2.0 * math.pi * r_side_ohm * c_side_f)
# twint_R_from_f0(50.0, 100e-9) -> ~31831 Ом
# twint_f0(31830.0, 100e-9)     -> ~50.0 Гц  ✓
