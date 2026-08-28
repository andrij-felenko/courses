# Полярний бік обернення: |Y| = 1/|Z|, φ_Y = −φ_Z
import cmath
import math

R, X = 30.0, 40.0                       # Ом
Z = complex(R, X)                       # імпеданс як комплексне число

Zmag = abs(Z)                           # |Z| = 50 Ом
phiZ = cmath.phase(Z)                   # кут імпедансу (рад), +53.13°

Y = 1 / Z                               # обернення робить сама мова
Ymag = abs(Y)                           # |Y| = 1/50 = 0.0200 См
phiY = cmath.phase(Y)                   # кут адмітансу = −φ_Z, −53.13°

print(f"|Z| = {Zmag:.1f} Ом,  phiZ = {math.degrees(phiZ):+.2f} deg")
print(f"|Y| = {Ymag:.4f} См,  phiY = {math.degrees(phiY):+.2f} deg")
