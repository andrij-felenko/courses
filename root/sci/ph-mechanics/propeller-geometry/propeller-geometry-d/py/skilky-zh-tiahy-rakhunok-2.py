import math


# Кут установки перерізу лопаті на радіусі r за геометричним кроком P.
# tan(beta) = P / (2·π·r)  →  beta = atan( P / (2·π·r) )
def blade_angle_deg(pitch_m, r_m):
    beta = math.atan(pitch_m / (2.0 * math.pi * r_m))
    return math.degrees(beta)


r75 = 0.75 * 0.064                              # 0.048 м — переріз 75 % радіуса
beta = blade_angle_deg(0.114, r75)
# tan β = 0.114 / (2·π·0.048) = 0.114 / 0.3016 = 0.378
# β = atan(0.378) ≈ 20.7°
