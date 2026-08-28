# Параметри реального конденсатора → точки галочки |Z(f)|.
# f0 — дно (резонанс), |Z|min = ESR, плюс DF і Q на заданій частоті.
import math


# модуль повного опору в одній точці частоти: |Z| = sqrt(ESR^2 + (wL - 1/wC)^2)
def z_mag(f, C, L, esr):
    w = 2.0 * math.pi * f
    X = w * L - 1.0 / (w * C)   # чиста реактивність: індуктивна − ємнісна
    return math.sqrt(esr * esr + X * X)


C = 100e-9         # 100 нФ
L = 2e-9           # 2 нГ паразитної індуктивності
esr = 0.03         # 0.03 Ом
f_work = 100e3     # робоча частота 100 кГц

f0 = 1.0 / (2.0 * math.pi * math.sqrt(L * C))   # дно галочки
Xc = 1.0 / (2.0 * math.pi * f_work * C)          # ємнісний опір на 100 кГц
DF = esr / Xc                                     # коефіцієнт втрат
Q = Xc / esr                                      # добротність = 1/DF

print(f"f0      = {f0 / 1e6:.2f} MHz")
print(f"|Z|@f0  = {z_mag(f0, C, L, esr):.3f} Ohm  (= ESR)")
print(f"|Z|@100kHz = {z_mag(f_work, C, L, esr):.2f} Ohm")
print(f"DF      = {DF:.5f}")
print(f"Q       = {Q:.0f}")
