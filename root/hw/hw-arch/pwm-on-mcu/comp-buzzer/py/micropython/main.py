from machine import Pin, PWM
from time import sleep_ms

buz = PWM(Pin(4), freq=2000, duty=512)   # ніжка; стартова частота 2000 Гц; 50% (з 1023)
while True:
    buz.duty(512)
    buz.freq(440)                # нота «ля» — 440 Гц
    sleep_ms(300)
    buz.freq(880)                # на октаву вище
    sleep_ms(300)
    buz.duty(0)                  # тиша (шпаруватість 0)
    sleep_ms(400)
