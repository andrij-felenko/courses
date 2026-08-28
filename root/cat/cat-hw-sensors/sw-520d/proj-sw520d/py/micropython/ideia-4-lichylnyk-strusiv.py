from machine import Pin
import time

PIN_SW    = 2
PIN_LED   = 13
ACTIVE    = 0
DEBOUNCE  = 40                         # глухе вікно проти брязкоту, мс
WINDOW    = 1000                       # вікно підрахунку, мс
THRESHOLD = 5                          # поріг «сильної вібрації» за вікно

sw  = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)
led = Pin(PIN_LED, Pin.OUT)

last_stable  = False
last_edge_ms = 0

count     = 0                          # струсів у поточному вікні
window_ms = 0                          # початок поточного вікна

def shock_detected():                  # той самий неблокувальний дебаунс
    global last_stable, last_edge_ms
    raw = (sw.value() == ACTIVE)
    if raw == last_stable:
        return False
    if time.ticks_diff(time.ticks_ms(), last_edge_ms) < DEBOUNCE:
        return False
    last_edge_ms = time.ticks_ms()
    last_stable = raw
    return raw                         # True лише на замиканні

window_ms = time.ticks_ms()

while True:
    # 1) лічимо підтверджені струси
    if shock_detected():
        count += 1

    # 2) щойно вікно (1 с) вичерпалось — оцінюємо й починаємо нове
    if time.ticks_diff(time.ticks_ms(), window_ms) >= WINDOW:
        print("струсів за секунду:", count)

        led.value(1 if count >= THRESHOLD else 0)   # тривога?

        count = 0                      # скидаємо лічильник
        window_ms = time.ticks_ms()    # нове вікно
