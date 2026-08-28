from machine import Pin
import time

BUZZER  = 8
PIN_BTN = 2                        # кнопка між піном і землею

HALF_MS = 100                      # тривалість кожної півфази (біп / пауза)

buzzer = Pin(BUZZER, Pin.OUT)
btn    = Pin(PIN_BTN, Pin.IN, Pin.PULL_UP)  # у спокої 1; натиск → 0
buzzer.value(0)

steps_left = 0                     # скільки перемикань стану ще лишилось
sound_on   = False
last_flip  = time.ticks_ms()

# Запустити серію з n біпів. Один біп = 2 перемикання стану.
def beep_series(n):
    global steps_left, last_flip, sound_on
    steps_left = n * 2             # n біпів = 2·n змін стану
    last_flip  = time.ticks_ms()
    sound_on   = True              # перший крок — одразу вмикаємо
    buzzer.value(1)

def series_busy():
    return steps_left > 0

was_pressed = False
while True:
    now = time.ticks_ms()

    # 1) подія: натиск запускає серію, лише коли попередня добігла
    pressed = (btn.value() == 0)
    if pressed and not was_pressed and not series_busy():
        beep_series(3)             # три біпи на помилку
    was_pressed = pressed

    # 2) неблокуючий прогін серії
    if steps_left > 0 and time.ticks_diff(now, last_flip) >= HALF_MS:
        last_flip = now
        steps_left -= 1
        if steps_left == 0:
            sound_on = False       # остання фаза — гарантовано гасимо
        else:
            sound_on = not sound_on
        buzzer.value(1 if sound_on else 0)
