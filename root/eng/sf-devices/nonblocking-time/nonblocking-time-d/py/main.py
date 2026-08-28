import time

def millis():
    return time.monotonic_ns() // 1_000_000   # мс від старту

last_blink = 0
last_read  = 0
blink_interval = 500   # мс
read_interval  = 100   # мс

while True:
    now = millis()

    if now - last_blink >= blink_interval:   # діло 1: блимати
        last_blink += blink_interval
        led_state = not led_state
        set_led(led_state)

    if now - last_read >= read_interval:     # діло 2: опитати давач
        last_read += read_interval
        read_sensor()

    # кнопки й будь-що інше — теж тут, нічого не блокує
