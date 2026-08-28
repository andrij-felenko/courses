from machine import Pin
import time

sw  = Pin(2, Pin.IN, Pin.PULL_UP)  # внутрішня підтяжка: спокій = 1
led = Pin(25, Pin.OUT)             # вбудований світлодіод

while True:
    # активний НУЛЬ: подія = 0 (кулька замкнула на землю)
    if sw.value() == 0:
        led.on()
        time.sleep_ms(50)          # грубий дебаунс: перечекати брязкіт кульки
    else:
        led.off()
