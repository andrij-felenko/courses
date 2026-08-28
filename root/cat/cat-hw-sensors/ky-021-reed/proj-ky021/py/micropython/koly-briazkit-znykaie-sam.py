from machine import Pin, disable_irq, enable_irq
import time

PIN_REED    = 4
DEBOUNCE_MS = 10

revolutions  = 0                  # змінюється в обробнику переривання
last_edge_ms = 0

def on_reed_fall(pin):            # обробник переривання (ISR)
    global revolutions, last_edge_ms
    now = time.ticks_ms()         # ticks_ms() усередині ISR читати можна
    if time.ticks_diff(now, last_edge_ms) >= DEBOUNCE_MS:  # той самий таймерний дебаунс
        revolutions += 1
        last_edge_ms = now

reed = Pin(PIN_REED, Pin.IN)
# край HIGH→LOW (магніт з'явився) смикає on_reed_fall()
reed.irq(trigger=Pin.IRQ_FALLING, handler=on_reed_fall)

last_report = 0
while True:
    if time.ticks_diff(time.ticks_ms(), last_report) >= 1000:
        last_report = time.ticks_ms()
        state = disable_irq()     # читаємо лічбу атомарно
        snapshot = revolutions
        enable_irq(state)
        print("обертів:", snapshot)
