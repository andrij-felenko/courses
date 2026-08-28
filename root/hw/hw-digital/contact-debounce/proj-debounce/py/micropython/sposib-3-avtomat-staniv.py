from machine import Pin
from time import ticks_ms, ticks_diff

T_MS = 20
btn = Pin(4, Pin.IN, Pin.PULL_UP)

STABLE, SUSPECT = 0, 1
st = STABLE
stable = 1                           # підтверджений рівень
t0 = 0                               # коли увійшли в SUSPECT

def debounce_fsm():
    global st, stable, t0
    s = btn.value()
    if st == STABLE:
        if s != stable:              # помітили зміну — під підозру
            st = SUSPECT
            t0 = ticks_ms()
    elif st == SUSPECT:
        if s == stable:              # рівень повернувся → хибна тривога
            st = STABLE
        elif ticks_diff(ticks_ms(), t0) >= T_MS:  # устояв усе вікно → подія
            stable = s
            st = STABLE
            if s == 0:
                on_press()
