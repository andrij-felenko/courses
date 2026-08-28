from machine import Pin, PWM
from time import ticks_ms, ticks_diff

SERVO_PIN = 18
NEUTRAL_US = 1520
US_PER_DEG = 11.1
MIN_US, MAX_US = 1100, 1940
FRAME_MS = 20                  # крок часу = кадр серва (50 Гц)

servo = PWM(Pin(SERVO_PIN), freq=50)

cur_deg = 0.0                  # де вал зараз
tgt_deg = 0.0                  # куди хочемо
step_deg = 1.0                 # приріст на кадр -> швидкість
last_frame = ticks_ms()

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def apply_deg(deg):
    us = clamp(NEUTRAL_US + int(deg * US_PER_DEG), MIN_US, MAX_US)
    servo.duty_ns(us * 1000)

def service_move():
    global cur_deg, last_frame
    now = ticks_ms()
    if ticks_diff(now, last_frame) < FRAME_MS:   # ще не час на новий крок
        return
    last_frame = now
    diff = tgt_deg - cur_deg
    if abs(diff) <= step_deg:
        cur_deg = tgt_deg                        # дійшли — сісти точно на ціль
    else:
        cur_deg += step_deg if diff > 0 else -step_deg
    apply_deg(cur_deg)

def move_to(deg):
    global tgt_deg
    tgt_deg = deg                                # лише задати ціль

apply_deg(0)

while True:
    if cur_deg == tgt_deg:                       # гойдати між −30 і +30
        move_to(+30 if tgt_deg <= 0 else -30)
    service_move()                               # тут відбувається плавний крок
    # ... цикл вільний робити будь-що інше ...
