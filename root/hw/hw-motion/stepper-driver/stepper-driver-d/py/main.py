# Керування кроковим драйвером через два піни STEP/DIR (RPi.GPIO).
import RPi.GPIO as GPIO
import time

PIN_STEP = 4
PIN_DIR = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_STEP, GPIO.OUT)
GPIO.setup(PIN_DIR, GPIO.OUT)

def step_pulse():                    # один імпульс = один крок
    GPIO.output(PIN_STEP, GPIO.HIGH)
    time.sleep(3e-6)                 # коротка «полиця» — драйвер ловить фронт
    GPIO.output(PIN_STEP, GPIO.LOW)
    time.sleep(3e-6)

def move_steps(n, forward):
    GPIO.output(PIN_DIR, GPIO.HIGH if forward else GPIO.LOW)  # напрямок читання таблиці
    for _ in range(n):
        step_pulse()
        time.sleep(1200e-6)          # пауза між кроками задає швидкість

def quarter_turn():
    move_steps(200 // 4, True)       # 50 кроків уперед = 90°
