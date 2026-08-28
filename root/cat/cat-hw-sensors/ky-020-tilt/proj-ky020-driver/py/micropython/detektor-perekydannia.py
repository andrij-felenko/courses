from machine import Pin
import time

TILT     = 2
BUZZ     = 8                             # зумер / реле (окрема нога, не S!)
SETTLE   = 30                           # мс: гасіння брязкоту
ALARM_MS = 800                          # мс: скільки НАХИЛ має триматися до тривоги

tilt = Pin(TILT, Pin.IN, Pin.PULL_UP)
buzz = Pin(BUZZ, Pin.OUT)

last_raw = stable_state = tilt.value()
last_change_ms  = 0
tilted_since_ms = 0                      # коли розпочався ПОТОЧНИЙ усталений нахил
alarm_on = False

while True:
    now = time.ticks_ms()

    # 1) гасіння брязкоту → чистий stable_state
    raw = tilt.value()
    if raw != last_raw:
        last_change_ms = now
        last_raw = raw
    if time.ticks_diff(now, last_change_ms) > SETTLE and raw != stable_state:
        stable_state = raw
        if stable_state == 0:
            tilted_since_ms = now       # нахил тільки-но став усталеним

    # 2) тривога — лише якщо усталений нахил тримається довше за ALARM_MS
    long_tilt = (stable_state == 0 and
                 time.ticks_diff(now, tilted_since_ms) > ALARM_MS)
    if long_tilt and not alarm_on:
        alarm_on = True
        buzz.value(1)
        print("ТРИВОГА: пристрій лежить набік!")
    elif not long_tilt and alarm_on and stable_state == 1:
        alarm_on = False                # підняли назад — знімаємо тривогу
        buzz.value(0)
        print("норма: пристрій вирівняно")
