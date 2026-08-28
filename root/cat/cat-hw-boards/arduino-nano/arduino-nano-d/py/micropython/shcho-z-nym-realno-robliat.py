# Класичний "blink": вбудований світлодіод на D13 моргає раз на секунду.
from machine import Pin
from time import sleep_ms

led = Pin(13, Pin.OUT)               # D13 на Nano

while True:
    led.on()                         # засвітити
    sleep_ms(500)                    # почекати 0.5 с
    led.off()                        # згасити
    sleep_ms(500)
