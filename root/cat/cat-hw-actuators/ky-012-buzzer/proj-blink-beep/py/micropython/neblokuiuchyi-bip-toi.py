from machine import Pin
import time

buzzer = Pin(8, Pin.OUT)
buzzer.value(0)

beeping   = False                  # чи зараз триває біп
beep_until = 0                     # момент (мс), коли біп треба вимкнути

# Запустити біп на ms мс і ОДРАЗУ повернути керування.
def beep_start(ms):
    global beeping, beep_until
    buzzer.value(1)                # вмикаємо звук зараз
    beeping = True
    beep_until = time.ticks_add(time.ticks_ms(), ms)  # КОЛИ вимкнути

# Смикати в КОЖНІЙ ітерації: гасить біп, коли настав час. Нічого не блокує.
def beep_update():
    global beeping
    if beeping and time.ticks_diff(time.ticks_ms(), beep_until) >= 0:
        buzzer.value(0)
        beeping = False

last_event = time.ticks_ms()
while True:
    now = time.ticks_ms()
    # приклад події: раз на 2 с пускаємо короткий біп
    if time.ticks_diff(now, last_event) >= 2000:
        last_event = now
        beep_start(80)             # пустили й полетіли далі — цикл не завмер

    beep_update()                  # єдиний обов'язок біпа щоцикл
    # ...тут будь-яка інша логіка, вона не блокована
