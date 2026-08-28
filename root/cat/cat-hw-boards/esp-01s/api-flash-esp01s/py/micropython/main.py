# Найдрібніший скрипт: блимаємо вбудованим синім LED на ESP-01S.
# LED сидить на GPIO2 і УВІМКНЕНО ЗА НИЗЬКИМ РІВНЕМ:
#   value(0) → світиться,   value(1) → гасне.

from machine import Pin
from time import sleep_ms

led = Pin(2, Pin.OUT)      # GPIO2 — до нього припаяно синій світлодіод
led.value(1)               # старт із погашеним (1 = вимкнено!)

while True:
    led.value(0)           # світиться
    sleep_ms(500)          # 0.5 с
    led.value(1)           # гасне
    sleep_ms(500)
