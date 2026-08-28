# KY-012 активний зумер.  S → пін 8;  − → GND;  середній штир — нікуди.
from machine import Pin
import time

buzzer = Pin(8, Pin.OUT)      # сигнальний штир — як звичайний вихід

while True:
    buzzer.value(1)           # одиниця → транзистор відкрився → пищить (~2.5 кГц)
    time.sleep_ms(200)        # 0.2 с звуку
    buzzer.value(0)           # нуль → тиша
    time.sleep_ms(1800)       # 1.8 с паузи
