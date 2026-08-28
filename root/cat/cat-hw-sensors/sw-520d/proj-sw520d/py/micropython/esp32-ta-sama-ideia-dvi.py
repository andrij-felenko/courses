# ── варіант під ESP32 ──
from machine import Pin

PIN_SW = 4                             # на ESP32 годиться майже будь-який GPIO

shock_flag = False

# у MicroPython обробник кладеться у RAM автоматично — окремого IRAM_ATTR не треба
def isr_shock(pin):
    global shock_flag
    shock_flag = True

sw = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)
sw.irq(trigger=Pin.IRQ_FALLING, handler=isr_shock)

while True:
    if shock_flag:
        shock_flag = False
        print("ESP32 прокинувся від струсу!")
