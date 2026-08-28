from machine import Pin

PIN_SW  = 2                        # вивід давача (другий — на GND)
PIN_LED = 13                       # вбудований світлодіод

ACTIVE  = 0                        # активний нуль: подія = 0 (LOW)

sw  = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)   # спокій = 1, замикання кульки = 0
led = Pin(PIN_LED, Pin.OUT)

while True:
    tilted = (sw.value() == ACTIVE)      # читаємо «чи замкнено»
    led.value(1 if tilted else 0)
