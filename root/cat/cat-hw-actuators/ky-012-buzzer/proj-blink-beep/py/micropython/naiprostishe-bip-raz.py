from machine import Pin
import time

buzzer = Pin(8, Pin.OUT)           # S модуля на цифровому виході
buzzer.value(0)                    # старт із тиші

# Один біп заданої довжини (мс). Блокуючий.
def beep(ms):
    buzzer.value(1)                # одиниця → транзистор відкрився → пищить
    time.sleep_ms(ms)
    buzzer.value(0)                # тиша

while True:
    beep(80)                       # короткий «тик»
    time.sleep_ms(2000)
