from machine import ADC, Pin
from math import log
from time import sleep_ms

R_FIXED = 10000.0   # сталий резистор на модулі, Ом
R25     = 10000.0   # опір термістора за 25 °C
BETA    = 3950.0    # B-параметр термістора, K
T25     = 298.15    # 25 °C у кельвінах

ntc = ADC(Pin(34))          # сигнал S на ADC1-здатному піні ESP32
ntc.atten(ADC.ATTN_11DB)    # повний діапазон входу ~0..3.3 В

def read_temp_c():
    raw = ntc.read_u16()            # 0..65535 незалежно від розрядності АЦП
    ratio = raw / 65535.0           # частка шкали = U_S / Vcc

    # Термістор у ВЕРХНЬОМУ плечі (між + і S), сталий резистор — знизу:
    #   U_S/Vcc = R_fixed / (R_ntc + R_fixed)  →  R_ntc = R_fixed*(1/ratio − 1)
    r_ntc = R_FIXED * (1.0 / ratio - 1.0)

    # B-формула: з опору назад у температуру (Vcc скоротилося саме)
    inv_t = 1.0 / T25 + log(r_ntc / R25) / BETA
    return 1.0 / inv_t - 273.15     # назад у °C

while True:
    print("{:.1f} C".format(read_temp_c()))
    sleep_ms(500)
