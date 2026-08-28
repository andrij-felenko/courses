# ESP32 (MicroPython): читати ємнісний щуп правильним аналоговим трактом.
from machine import Pin, ADC
import time

power = Pin(25, Pin.OUT)                # живлення щупа з GPIO25
soil  = ADC(Pin(34))                    # AOUT на GPIO34 — це ADC1 (важливо, див. нижче)
soil.width(ADC.WIDTH_12BIT)             # 0…4095
soil.atten(ADC.ATTN_11DB)               # діапазон входу ≈ 0…3.1 В

# калібрування для ESP32 — інші числа, бо 12 біт! зняти на самому ESP32:
AIR   = 2600                            # сухо (щуп у повітрі)
WATER = 1300                            # мокро (щуп у воді)

def read_avg(adc, n=16):
    total = 0
    for _ in range(n):
        total += adc.read()
        time.sleep_ms(2)
    return total // n

def to_percent(raw):
    pct = (raw - AIR) * 100 // (WATER - AIR)   # AIR→0%, WATER→100%
    return max(0, min(100, pct))               # затиск у 0…100

power.value(0)
while True:
    power.value(1)                      # ожив генератор
    time.sleep_ms(50)                   # усталення
    raw = read_avg(soil)
    power.value(0)                      # знеструмили

    pct = to_percent(raw)
    print("raw={}  moisture={}%".format(raw, pct))
    time.sleep_ms(2000)
