# ESP32 (MicroPython): ШІМ підсвітки на ніжку EN струмового драйвера.
# Ціль: частота вище 1250 Гц (зона безпеки IEEE 1789) + якнайбільше кроків.
from machine import Pin, PWM

FREQ = 2000                # 2 кГц — вище порога 1250 Гц
STEPS = 4096               # 12-бітний діапазон кроків яскравості (0..4095)
bl = None

def backlight_init():
    global bl
    bl = PWM(Pin(25), freq=FREQ)   # LEDC сам добирає розрядність під частоту

def backlight_set(level):          # level: 0..4095
    # machine.PWM подає шпаруватість як 16-біт, тож масштабуємо 12-біт крок у duty_u16.
    bl.duty_u16(level * 65535 // (STEPS - 1))
