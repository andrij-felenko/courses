from machine import Pin
import time

knock = Pin(2, Pin.IN, Pin.PULL_UP)   # підтяжка вгору: спокій = 1, удар тягне до 0
led = Pin(13, Pin.OUT)                # вбудований світлодіод
LOCKOUT = 250                         # глухе вікно після стуку, мс

last_knock = 0                        # час останнього зарахованого стуку
count = 0                             # лічильник стуків

while True:
    now = time.ticks_ms()
    # активний-НИЗЬКО: удар — це коли вхід просів у 0
    if knock.value() == 0 and time.ticks_diff(now, last_knock) > LOCKOUT:
        last_knock = now
        count += 1
        led.value(1)
        print("стук #", count)
    # гасимо світлодіод трохи згодом після спалаху
    if time.ticks_diff(time.ticks_ms(), last_knock) > 60:
        led.value(0)
