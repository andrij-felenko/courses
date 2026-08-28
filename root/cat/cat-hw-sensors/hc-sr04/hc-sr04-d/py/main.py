import time
import RPi.GPIO as GPIO

TRIG_PIN = 9
ECHO_PIN = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_cm():
    # 1. Спусковий імпульс: 10 мкс високого рівня на TRIG
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(2e-6)
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(10e-6)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # 2. Ширина високого імпульсу на ECHO = час польоту в мкс.
    #    Тайм-аут 30000 мкс, щоб не зависнути, коли луни немає.
    deadline = time.monotonic() + 0.030
    while GPIO.input(ECHO_PIN) == 0:
        if time.monotonic() > deadline:
            return -1            # нічого не почули (порожньо/далеко)
    start = time.monotonic()
    while GPIO.input(ECHO_PIN) == 1:
        if time.monotonic() > deadline:
            return -1
    t = (time.monotonic() - start) * 1_000_000  # с → мкс

    return int(t // 58)          # мкс → см

while True:
    cm = measure_cm()
    if cm < 0:
        print("out of range")
    else:
        print(cm, "cm")
    time.sleep(0.060)            # пауза між вимірами ≥ 60 мс
