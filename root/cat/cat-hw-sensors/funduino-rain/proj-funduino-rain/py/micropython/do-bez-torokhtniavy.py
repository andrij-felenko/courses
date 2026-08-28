from machine import Pin
import time

RAIN = Pin(2, Pin.IN)               # цифровий вихід DO давача
LED  = Pin(13, Pin.OUT)             # вбудований світлодіод плати
SETTLE = 400                        # скільки стан має протриматися, мс

raining   = False                   # поточний ПІДТВЕРДЖЕНИЙ стан
candidate = False                   # стан, який щойно побачили на нозі
changed_at = time.ticks_ms()        # коли кандидат уперше з'явився

while True:
    # DO: 0 = дощ, 1 = сухо. Робимо булеве «зараз дощить?»
    now = (RAIN.value() == 0)

    # показ змінився — запам'ятовуємо як кандидата й засікаємо час
    if now != candidate:
        candidate = now
        changed_at = time.ticks_ms()

    # приймаємо новий стан, ЛИШЕ коли кандидат протримався SETTLE мс —
    # це програмний гістерезис проти торохтняви межі
    if candidate != raining and time.ticks_diff(time.ticks_ms(), changed_at) > SETTLE:
        raining = candidate
        LED.value(raining)
        print("дощ почався" if raining else "дощ скінчився")
    # програма НЕ спить: сюди можна вставити будь-яку іншу роботу
