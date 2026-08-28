from machine import Pin
import time

TILT   = 2
SETTLE = 30

pin_changed    = False                  # прапорець з ISR
last_change_ms = 0
tilt_count     = 0

tilt = Pin(TILT, Pin.IN, Pin.PULL_UP)
last_raw = stable_state = tilt.value()

def on_edge(pin):                        # ISR — коротка, як постріл
    global pin_changed
    pin_changed = True                   # жодного print, читання-логіки, sleep тут!

# на будь-який фронт
tilt.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge)

while True:
    if pin_changed:                      # ISR щось помітила
        pin_changed = False
        raw = tilt.value()
        if raw != last_raw:
            last_change_ms = time.ticks_ms()
            last_raw = raw
    # гасіння крутиться в циклі, спокійно
    if time.ticks_diff(time.ticks_ms(), last_change_ms) > SETTLE and last_raw != stable_state:
        stable_state = last_raw
        if stable_state == 0:
            tilt_count += 1
            print("нахилів:", tilt_count)
