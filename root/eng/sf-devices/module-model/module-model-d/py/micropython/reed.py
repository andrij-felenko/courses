# reed.py — модуль давача: деталі сховано за іменем модуля
from machine import Pin

_REED_PIN = 4          # до якого піна припаяно — деталь модуля
_ACTIVE_LEVEL = 0      # геркон active-low: 0 = замкнено

# _pin з підкресленням → приватна деталь модуля: інкапсуляція
# підтяжка тримає HIGH, поки давач не замкне лінію в LOW
_pin = Pin(_REED_PIN, Pin.IN, Pin.PULL_UP)

def reed_init():
    # ніжку вже налаштовано вище, при імпорті модуля
    pass

def reed_is_closed():
    return _pin.value() == _ACTIVE_LEVEL   # ховаємо «0 vs 1» від світу
