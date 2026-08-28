from machine import Pin
import time

rain = Pin(2, Pin.IN)   # push-pull-вихід LM358 → підтяжка не потрібна
led = Pin(13, Pin.OUT)
SETTLE = 400            # скільки стан має протриматися (мс)

raining = False         # поточний підтверджений стан
candidate = False       # стан, який щойно побачили
changed_at = 0          # коли кандидат уперше з'явився

while True:
    # DO: 0 = дощ, 1 = сухо. Робимо булеве «зараз дощить?»
    now = (rain.value() == 0)

    # якщо показ змінився — запам'ятовуємо як кандидата й засікаємо час
    if now != candidate:
        candidate = now
        changed_at = time.ticks_ms()

    # приймаємо новий стан, лише коли кандидат протримався SETTLE мс —
    # це програмний гістерезис проти торохтняви на межі (LM358 без гістерезису)
    if candidate != raining and time.ticks_diff(time.ticks_ms(), changed_at) > SETTLE:
        raining = candidate
        led.value(1 if raining else 0)
        print("дощ почався" if raining else "дощ скінчився")
