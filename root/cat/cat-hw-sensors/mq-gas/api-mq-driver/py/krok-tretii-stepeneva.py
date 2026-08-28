import math
from collections import namedtuple

# Крива газу: {x = lg(ppm), y = lg(Rₛ/R₀) у опорній точці, slope = нахил}.
# Значення для MQ-2 з коду Sandbox Electronics (зняті з графіків даташита).
MqCurve = namedtuple("MqCurve", ("x", "y", "slope"))

LPG_CURVE   = MqCurve(2.3, 0.21, -0.47)
CO_CURVE    = MqCurve(2.3, 0.72, -0.34)
SMOKE_CURVE = MqCurve(2.3, 0.53, -0.44)


def mq_ppm(rs_r0, c):
    """Відношення Rₛ/R₀ → ppm за степеневою кривою (у точковій формі)."""
    # lg(ppm) = x + (lg(Rₛ/R₀) − y) / slope,  далі 10 у цей степінь
    lg_ppm = c.x + (math.log10(rs_r0) - c.y) / c.slope
    return 10.0 ** lg_ppm
