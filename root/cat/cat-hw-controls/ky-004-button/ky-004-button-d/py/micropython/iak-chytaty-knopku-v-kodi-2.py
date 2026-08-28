from machine import Pin
from time import sleep_ms

btn = Pin(2, Pin.IN)             # KY-004 має підтяжку на платі

sleep_ms(20)                     # дати лінії влягтися
idle = btn.value()               # що читається у спокої — те й «не натиснуто»
# idle==0 → плата pull-down;  idle==1 → плата pull-up. Далі байдуже.

last = idle                      # попередній усталений стан
presses = 0

while True:
    now = btn.value()

    if now != last:              # рівень змінився — можливо, натиск або брязкіт
        sleep_ms(15)             # антибрязкіт: чекаємо, поки контакт устоїться
        now = btn.value()        # перечитуємо усталений рівень
        if now != last:          # зміна справжня
            last = now
            if now != idle:      # перейшли зі стану спокою — це НАТИСК
                presses += 1
                print(presses)
