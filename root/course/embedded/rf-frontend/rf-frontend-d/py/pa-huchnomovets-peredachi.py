# Перевірка «на пальцях»: у скільки разів далі добиває сигнал
import math

def range_gain(gain_db):
    # потужність ~ 1/d², отже d ~ 1/sqrt(P);
    # +gain_db децибел => множник потужності 10^(gain/10)
    power_ratio = 10 ** (gain_db / 10)  # 21 dB -> ×125.9
    return math.sqrt(power_ratio)       # дальність ~ sqrt

# range_gain(21.0) ≈ 11.2  → приблизно в 11 разів далі
