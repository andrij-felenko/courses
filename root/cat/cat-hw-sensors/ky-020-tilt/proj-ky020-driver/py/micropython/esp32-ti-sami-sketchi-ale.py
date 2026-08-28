# ESP32 (MicroPython): живлення давача — 3.3 В! Сигнал S — на звичайну ногу з підтяжкою.
from machine import Pin
import micropython, time
micropython.alloc_emergency_exception_buf(100)   # аби бачити помилки з ISR

TILT   = 14                             # звичайний GPIO (НЕ 34–39): має PULL_UP
SETTLE = 30

pin_changed    = False                  # спільна з ISR
last_change_ms = 0
tilt_count     = 0

tilt = Pin(TILT, Pin.IN, Pin.PULL_UP)   # на GPIO14 підтяжка є; на 34–39 її НЕ буде
last_raw = stable_state = tilt.value()

def on_edge(pin):                        # у MicroPython обробник уже в IRAM — IRAM_ATTR не потрібен
    global pin_changed
    pin_changed = True                   # лише прапорець, нічого важкого

tilt.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=on_edge)

while True:
    if pin_changed:
        pin_changed = False
        raw = tilt.value()
        if raw != last_raw:
            last_change_ms = time.ticks_ms()
            last_raw = raw
    if time.ticks_diff(time.ticks_ms(), last_change_ms) > SETTLE and last_raw != stable_state:
        stable_state = last_raw
        if stable_state == 0:
            tilt_count += 1
            print("нахилів:", tilt_count)
