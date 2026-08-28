from machine import Pin
import time

btn = Pin(2, Pin.IN, Pin.PULL_UP)   # підтяжка до плюса: спокій = HIGH
led = Pin(13, Pin.OUT)

led_on = False          # поточний стан світлодіода
prev = 1                # попередній рівень піна (1 = відпущено)

while True:
    now = btn.value()                   # 0 = натиснуто, 1 = відпущено
    if prev == 1 and now == 0:          # спіймали перехід «відпущено → натиснуто»
        led_on = not led_on             # перемкнули стан на фронті натиску
        led.value(led_on)
        time.sleep_ms(20)               # груба пауза, щоб проскочити брязкіт
    prev = now
