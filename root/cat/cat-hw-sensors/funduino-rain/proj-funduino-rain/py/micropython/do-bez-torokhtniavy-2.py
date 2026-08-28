from machine import Pin
import time

RAIN = Pin(4, Pin.IN)               # DO на GPIO4
LED  = Pin(2, Pin.OUT)              # вбудований світлодіод (на більшості плат GPIO2)
SETTLE = 400

raining, candidate = False, False
changed_at = time.ticks_ms()

while True:
    now = (RAIN.value() == 0)
    if now != candidate:
        candidate = now
        changed_at = time.ticks_ms()
    if candidate != raining and time.ticks_diff(time.ticks_ms(), changed_at) > SETTLE:
        raining = candidate
        LED.value(raining)
        print("дощ почався" if raining else "дощ скінчився")
