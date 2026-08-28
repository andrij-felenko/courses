HOLD_MS = 1000                           # тримати ≈1 c, щоб перемкнути

# Викликається періодично (напр., кожні 10 мс) з відомим dt_ms.
def safety_button_poll(dt_ms):
    global safety_on
    if safety_button_pressed():          # кнопку зараз натиснуто?
        safety_button_poll.held_ms += dt_ms
        if safety_button_poll.held_ms >= HOLD_MS:   # дотримали до порога —
            safety_on = not safety_on    # перемкнути стан безпеки
            safety_button_poll.held_ms = 0
            while safety_button_pressed():  # дочекатись відпускання,
                pass                        # щоб не перемкнути знову
    else:
        safety_button_poll.held_ms = 0   # відпустили рано — лічильник з нуля

safety_button_poll.held_ms = 0           # статичний лічильник між викликами
