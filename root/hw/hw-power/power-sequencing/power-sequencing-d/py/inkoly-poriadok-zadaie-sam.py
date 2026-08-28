from machine import Pin
import time

# Вивід EN кожного перетворювача керує його шиною: 1 — увімкнено.
en_sensors = Pin('B0', Pin.OUT)      # шина давачів, 1.8 В
en_radio   = Pin('B1', Pin.OUT)      # шина радіо, 3.3 В

def power_up_sequence():
    en_sensors.value(0)
    en_radio.value(0)                # старт: усе вимкнено

    en_sensors.value(1)              # 1) перша шина
    time.sleep_ms(5)                 #    пауза на усталення й inrush

    en_radio.value(1)                # 2) друга шина — лише тепер
    time.sleep_ms(5)

    radio_enable_interface()         # 3) дозвіл на обмін — останнім
