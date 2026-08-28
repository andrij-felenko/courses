from machine import Pin, PWM
from time import sleep_ms

SERVO_PIN = 18

# --- калібрування конкретного примірника ---
NEUTRAL_US = 1520      # знайдена нейтраль
US_PER_DEG = 11.1      # 1000 мкс на 90° ходу ≈ 11.1 мкс/°

# --- безпечне вікно, підтягнуте ВСЕРЕДИНУ від стопорів ---
MIN_US = 1100          # не 1000: запас до стопора
MAX_US = 1940          # не 2000: те саме з іншого боку

servo = PWM(Pin(SERVO_PIN), freq=50)

def write_us(us):
    servo.duty_ns(int(us) * 1000)

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

# Єдина точка входу: кут у градусах від центру -> безпечний імпульс.
def set_angle(deg):
    us = NEUTRAL_US + int(deg * US_PER_DEG)
    us = clamp(us, MIN_US, MAX_US)   # ГОЛОВНИЙ запобіжник
    write_us(us)

set_angle(0)                         # у центр

while True:
    set_angle(-30); sleep_ms(800)    # ліворуч
    set_angle(+30); sleep_ms(800)    # праворуч
    set_angle(+90); sleep_ms(800)    # ПРОСИМО забагато — але clamp врятує серво
