# Кільцевий: біжучий вогник на 4 світлодіодах (MicroPython).
# Стан САМ є маскою виходів — жодного декодування.
from machine import Pin

leds = [Pin(p, Pin.OUT) for p in (14, 27, 26, 25)]  # ніжки під виходи 0..3
ring = 0x1                                # старт: активний лише вихід 0

def ring_tick():
    global ring
    for i, led in enumerate(leds):
        led.value((ring >> i) & 0x1)      # виставляємо унітарний код прямо на ніжки
    carry = ring & 0x1                    # біт, що "випадає"
    ring = ((ring >> 1) | (carry << 3)) & 0xF   # той самий крок кільця, назад у Q3
