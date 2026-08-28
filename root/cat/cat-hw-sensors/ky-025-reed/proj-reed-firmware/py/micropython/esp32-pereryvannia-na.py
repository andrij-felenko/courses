from machine import Pin
import time

REED        = 4                  # D0 на GPIO4 (майже будь-яка нога годиться)

DEBOUNCE_MS = 30

counter    = 0
t_last_isr = 0

# ISR має бути короткою; @micropython.native тримає її швидкою (аналог IRAM_ATTR).
@micropython.native
def on_reed(pin):
    global counter, t_last_isr
    now = time.ticks_ms()
    if time.ticks_diff(now, t_last_isr) >= DEBOUNCE_MS:
        t_last_isr = now
        counter += 1

# у KY-025 підтяжка є на платі; для голого геркона — Pin.PULL_UP
reed = Pin(REED, Pin.IN, Pin.PULL_UP)
# Активний LOW → магніт дає спад → фронт спаду:
reed.irq(trigger=Pin.IRQ_FALLING, handler=on_reed)
print("ESP32: переривання на герконі увімкнено.")

shown = 0

while True:
    if counter != shown:
        shown = counter
        print("подій:", shown)
    # основний код вільний; наприклад, тут може крутитися Wi-Fi / дисплей
