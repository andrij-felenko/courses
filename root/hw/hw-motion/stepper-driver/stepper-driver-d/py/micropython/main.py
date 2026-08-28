# Керування кроковим драйвером через два піни STEP/DIR.
from machine import Pin
import time

step = Pin(4, Pin.OUT)
dir_ = Pin(5, Pin.OUT)

def step_pulse():                    # один імпульс = один крок
    step.value(1)
    time.sleep_us(3)                 # коротка «полиця» — драйвер ловить фронт
    step.value(0)
    time.sleep_us(3)

def move_steps(n, forward):
    dir_.value(1 if forward else 0)  # напрямок читання таблиці
    for _ in range(n):
        step_pulse()
        time.sleep_us(1200)          # пауза між кроками задає швидкість

def quarter_turn():
    move_steps(200 // 4, True)       # 50 кроків уперед = 90°
