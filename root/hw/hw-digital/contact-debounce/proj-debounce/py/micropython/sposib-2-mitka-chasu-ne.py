from machine import Pin
from time import ticks_ms, ticks_diff

T_MS = 20                            # вікно тиші, мс
btn = Pin(4, Pin.IN, Pin.PULL_UP)

last_raw = 1                         # попередній СИРИЙ рівень
stable   = 1                         # прийнятий стабільний рівень
t_change = 0                         # коли сирий рівень смикнувся востаннє

def debounce_poll():
    global last_raw, stable, t_change
    s = btn.value()
    if s != last_raw:                # рівень смикнувся — засікли час
        last_raw = s
        t_change = ticks_ms()
    # тиша протягом T і рівень НОВИЙ → це справжня подія
    if ticks_diff(ticks_ms(), t_change) >= T_MS and s != stable:
        stable = s
        if s == 0:
            on_press()
