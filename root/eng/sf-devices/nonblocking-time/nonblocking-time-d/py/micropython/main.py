import time
from machine import Pin

led = Pin(2, Pin.OUT)
led_state = 0

last_blink = 0
last_read  = 0
blink_interval = 500   # мс
read_interval  = 100   # мс

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_blink) >= blink_interval:   # діло 1: блимати
        last_blink = time.ticks_add(last_blink, blink_interval)
        led_state = not led_state
        led.value(led_state)

    if time.ticks_diff(now, last_read) >= read_interval:     # діло 2: опитати давач
        last_read = time.ticks_add(last_read, read_interval)
        read_sensor()

    # кнопки й будь-що інше — теж тут, нічого не блокує
