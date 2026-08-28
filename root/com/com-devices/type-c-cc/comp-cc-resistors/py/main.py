# Прочитати дозволений струм USB-C із напруги на активному CC.
# adc_read_mv(pin) повертає напругу на піні в мілівольтах.

from enum import Enum

class CcLevel(Enum):
    NONE    = 0   # нічого не під'єднано
    DEFAULT = 1   # звичайний USB (0.5 / 0.9 А)
    A1V5    = 2   # 1.5 А
    A3V0    = 3   # 3.0 А

def cc_decode(mv):
    if mv < 200:    return CcLevel.NONE     # < 0.20 В — нічого не під'єднано
    if mv < 660:    return CcLevel.DEFAULT  # 0.20–0.66 В — звичайний USB
    if mv < 1230:   return CcLevel.A1V5     # 0.66–1.23 В — 1.5 А
    return CcLevel.A3V0                      # > 1.23 В — повні 3.0 А

# Роз'єм реверсивний: активний той CC, на якому є напруга.
def usbc_read_profile():
    cc = max(adc_read_mv(PIN_CC1), adc_read_mv(PIN_CC2))  # живий пін — з вищою напругою
    return cc_decode(cc)
