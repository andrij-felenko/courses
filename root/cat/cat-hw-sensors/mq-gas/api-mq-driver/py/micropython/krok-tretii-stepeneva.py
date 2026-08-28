import math

# Крива газу: (x = lg(ppm), y = lg(Rₛ/R₀) у опорній точці, slope = нахил).
# Значення для MQ-2 з коду Sandbox Electronics (зняті з графіків даташита).
LPG_CURVE   = (2.3, 0.21, -0.47)
CO_CURVE    = (2.3, 0.72, -0.34)
SMOKE_CURVE = (2.3, 0.53, -0.44)


def mq_ppm(rs_r0, curve):
    # Відношення Rₛ/R₀ → ppm за степеневою кривою (у точковій формі).
    x, y, slope = curve
    # lg(ppm) = x + (lg(Rₛ/R₀) − y) / slope,  далі 10 у цей степінь
    lg_ppm = x + (math.log10(rs_r0) - y) / slope
    return 10.0 ** lg_ppm
