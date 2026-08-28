from machine import Pin
import time

PIN_SW   = 4
DEBOUNCE = 40                          # глухе вікно, мс

shock_flag  = False
last_isr_ms = 0

def isr_shock(pin):
    global shock_flag, last_isr_ms
    now = time.ticks_ms()              # у MicroPython ticks_ms() в обробнику безпечний
    if time.ticks_diff(now, last_isr_ms) < DEBOUNCE:
        return                         # ще брязкіт тієї ж події — ігноруємо
    last_isr_ms = now
    shock_flag = True

sw = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)
sw.irq(trigger=Pin.IRQ_FALLING, handler=isr_shock)
