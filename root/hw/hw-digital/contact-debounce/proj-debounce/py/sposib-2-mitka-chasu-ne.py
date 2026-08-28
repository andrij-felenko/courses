from time import monotonic

T = 0.020                            # вікно тиші, с

last_raw = HIGH                      # попередній СИРИЙ рівень
stable   = HIGH                      # прийнятий стабільний рівень
t_change = 0.0                       # коли сирий рівень смикнувся востаннє

def debounce_poll():
    global last_raw, stable, t_change
    s = digital_read(BTN_PIN)
    if s != last_raw:                # рівень смикнувся — засікли час
        last_raw = s
        t_change = monotonic()
    # тиша протягом T і рівень НОВИЙ → це справжня подія
    if monotonic() - t_change >= T and s != stable:
        stable = s
        if s == LOW:
            on_press()
