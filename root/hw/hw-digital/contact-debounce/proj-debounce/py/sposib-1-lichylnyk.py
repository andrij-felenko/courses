# Викликати рівно раз на тік (напр. кожну 1 мс із таймера).
N = 5                        # скільки однакових відліків = «стабільно»

cnt = 0                      # лічильник однакових відліків
prev = HIGH                  # що читали минулого тіку
stable = HIGH                # останній прийнятий стабільний рівень

def debounce_tick():
    global cnt, prev, stable
    s = digital_read(BTN_PIN)
    cnt = cnt + 1 if s == prev else 0    # той самий — рахуємо, інакше — скид
    prev = s
    if cnt >= N and s != stable:         # рівень устояв і він НОВИЙ
        stable = s
        if s == LOW:                     # фронт «відпущено → натиснуто»
            on_press()
