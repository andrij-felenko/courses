from machine import Pin
import time

REED        = 4                  # D0 давача на GPIO4
ACTIVE      = 0                  # ← активний рівень вашої плати (з розвідки): 0 = LOW

DEBOUNCE_MS = 30                 # «мертвий час» після краю: коротший сплеск — брязкіт

reed     = Pin(REED, Pin.IN)
counter  = 0                     # накопичені події
was_near = (reed.value() == ACTIVE)   # попередній стан геркона (для виявлення краю)
t_edge   = 0                     # коли востаннє прийняли зміну стану

print("Лічильник геркона готовий.")

while True:
    near = (reed.value() == ACTIVE)
    now = time.ticks_ms()

    # Реагуємо лише на ЗМІНУ стану і лише якщо від минулої зміни минув мертвий час.
    if near != was_near and time.ticks_diff(now, t_edge) >= DEBOUNCE_MS:
        t_edge   = now
        was_near = near

        if near:                          # край саме «нема → є» — це нова подія
            counter += 1
            print("клац! всього:", counter)
