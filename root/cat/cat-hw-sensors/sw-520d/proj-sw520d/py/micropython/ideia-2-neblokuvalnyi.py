from machine import Pin
import time

PIN_SW   = 2
PIN_LED  = 13
ACTIVE   = 0
DEBOUNCE = 40                      # «глухе» вікно, мс — довше за брязкіт кульки

sw  = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)
led = Pin(PIN_LED, Pin.OUT)

last_stable = False                # останній ПІДТВЕРДЖЕНИЙ стан (True = замкнено)
last_edge_ms = 0                   # коли востаннє прийняли зміну

# Повертає True рівно раз — у мить, коли давач ПІДТВЕРДЖЕНО замкнувся.
def shock_detected():
    global last_stable, last_edge_ms
    raw = (sw.value() == ACTIVE)   # сирий рівень, ще з брязкотом

    # якщо стан не змінився — нічого не робимо
    if raw == last_stable:
        return False

    # стан начебто змінився — але чи вже вийшли з «глухого» вікна?
    if time.ticks_diff(time.ticks_ms(), last_edge_ms) < DEBOUNCE:
        return False               # ще брязкіт — ігноруємо

    # зміна справжня: фіксуємо її й перезапускаємо вікно
    last_edge_ms = time.ticks_ms()
    last_stable = raw

    return raw                     # True лише на фронті «розімкнено → замкнено»

while True:
    if shock_detected():
        print("струс!")
        led.value(1)

    # ... тут програма робить решту справ, НЕ чекаючи на давач ...
    # напр. плавне «серцебиття» світлодіодом, опитування інших давачів, мережа
