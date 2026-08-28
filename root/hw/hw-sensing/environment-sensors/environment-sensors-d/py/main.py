import math

# точка роси (°C) з температури й відносної вологості — формула Магнуса
def dew_point(t_c, rh_pct):
    a, b = 17.62, 243.12                        # сталі Магнуса (над водою)
    gamma = math.log(rh_pct / 100.0) + a * t_c / (b + t_c)
    return b * gamma / (a - gamma)              # °C

# тепле сухе повітря: давач показує 30 °C, 26 % RH
td = dew_point(30.0, 26.0)                       # ≈ 8.4 °C
