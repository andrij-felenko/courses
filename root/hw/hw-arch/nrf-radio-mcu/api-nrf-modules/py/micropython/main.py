from machine import Pin
import time

LED_PIN = 17   # P0.17 — типовий LED на багатьох nRF52-модулях

# Конфігуруємо пін як вихід
led = Pin(LED_PIN, Pin.OUT)

while True:
    led.toggle()          # інвертуємо: 0→1→0→…
    time.sleep_ms(500)
    # Блимає = живлення, кварц 32 МГц, ядро й прошивка — живі.
    # BLE-стек вмикається окремо поверх цього каркасу.
