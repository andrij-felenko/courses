# ESP32 з MicroPython — клас PWM формує сигнал апаратно.
from machine import Pin, PWM
from time import sleep_ms, sleep

ESC_PIN   = 18
FREQ      = 50           # 50 Гц — стандарт ESC
PERIOD_US = 20_000       # період за 50 Гц

esc = PWM(Pin(ESC_PIN), freq=FREQ)

def write_us(us):
    # у MicroPython газ задають шпаристістю у нc: duty_ns(ширина_в_нс).
    esc.duty_ns(us * 1000)

# ── ОЗБРОЄННЯ: без нього ESC не запуститься ─────────────────────────────
write_us(1000)           # мінімальний газ = «стоп»
sleep(3)                 # дати ESC озброїтись

while True:
    # ── ПЛАВНИЙ РОЗГІН до половини газу ─────────────────────────────────
    for us in range(1000, 1501, 5):
        write_us(us)
        sleep_ms(20)
    write_us(1500)
    sleep(3)

    # ── ПЛАВНЕ ГАЛЬМУВАННЯ ──────────────────────────────────────────────
    for us in range(1500, 999, -5):
        write_us(us)
        sleep_ms(20)
    write_us(1000)       # повний стоп
    sleep(3)
