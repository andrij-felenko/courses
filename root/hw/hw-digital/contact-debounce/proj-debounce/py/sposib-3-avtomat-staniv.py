from time import monotonic

T = 0.020

STABLE, SUSPECT = 0, 1
st = STABLE
stable = HIGH                        # підтверджений рівень
t0 = 0.0                             # коли увійшли в SUSPECT

def debounce_fsm():
    global st, stable, t0
    s = digital_read(BTN_PIN)
    if st == STABLE:
        if s != stable:              # помітили зміну — під підозру
            st = SUSPECT
            t0 = monotonic()
    elif st == SUSPECT:
        if s == stable:              # рівень повернувся → хибна тривога
            st = STABLE
        elif monotonic() - t0 >= T:  # устояв усе вікно → подія
            stable = s
            st = STABLE
            if s == LOW:
                on_press()
