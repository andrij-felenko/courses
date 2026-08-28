# Викликати рівно раз на тік (напр. кожну 1 мс із таймера).
from machine import Pin

N = 5                        # скільки однакових відліків = «стабільно»
btn = Pin(4, Pin.IN, Pin.PULL_UP)

cnt = 0                      # лічильник однакових відліків
prev = 1                    # що читали минулого тіку
stable = 1                   # останній прийнятий стабільний рівень

def debounce_tick():
    global cnt, prev, stable
    s = btn.value()
    cnt = cnt + 1 if s == prev else 0    # той самий — рахуємо, інакше — скид
    prev = s
    if cnt >= N and s != stable:         # рівень устояв і він НОВИЙ
        stable = s
        if s == 0:                       # фронт «відпущено → натиснуто»
            on_press()
