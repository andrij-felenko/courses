import math

# ФНЧ Саллена–Кі, рівні резистори R1=R2=R; задаємо f0 і Q.
# З Q = 0.5*sqrt(C1/C2)  ->  C1/C2 = (2Q)^2
# З f0 = 1/(2*pi*R*sqrt(C1*C2)) -> sqrt(C1*C2) = 1/(2*pi*R*f0)

R  = 11000.0          # Ом
f0 = 1000.0           # Гц
Q  = 0.70710678       # Баттерворт

ratio   = (2.0 * Q) * (2.0 * Q)          # C1/C2 = 2.0
geomean = 1.0 / (2.0 * math.pi * R * f0) # √(C1·C2) ≈ 1.447e-8

C2 = geomean / math.sqrt(ratio)   # ≈ 1.02e-8 Ф ≈ 10 нФ
C1 = ratio  * C2                  # ≈ 2.05e-8 Ф ≈ 20 нФ
