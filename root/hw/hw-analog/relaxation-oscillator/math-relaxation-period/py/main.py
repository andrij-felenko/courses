# Період і резистор релаксаційного генератора з порогами 1/3 і 2/3 живлення.
# τ = R·C; кожна фаза = τ·ln2; період = 2·τ·ln2.
from math import log

LN2 = log(2)  # 0.6931472…


def relax_period(r_ohm, c_farad):      # період T, секунди
    return 2 * r_ohm * c_farad * LN2   # T = 2·R·C·ln2 ≈ 1.386·R·C


def relax_resistor(f_hz, c_farad):     # R під бажану частоту
    return 1 / (2 * LN2 * f_hz * c_farad)  # R = 1 / (2·ln2 · f · C)


# Приклад: 2 Гц при 1 мкФ
r = relax_resistor(2.0, 1.0e-6)        # ≈ 360 700 Ом → ставимо 360 кОм
