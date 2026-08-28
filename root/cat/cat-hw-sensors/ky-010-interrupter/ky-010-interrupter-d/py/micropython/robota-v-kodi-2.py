from machine import Pin
import time

PIN_S   = 2
BLOCKED = 1              # з калібрування вище
GUARD   = 3             # «мертвий час», мс — гасить дрижання на схилі

pin_s = Pin(PIN_S, Pin.IN)
count = 0
prev  = False           # попередній стан щілини
t_edge = 0              # час останнього зарахованого фронту

while True:
    now = (pin_s.value() == BLOCKED)
    t = time.ticks_ms()

    # цікавить лише фронт «вільно → перекрито» і не частіше, ніж раз на GUARD мс
    if now and not prev and time.ticks_diff(t, t_edge) > GUARD:
        count += 1
        t_edge = t
        print(count)
    prev = now
