from machine import Pin
import time

PIN_LED = 5
PIN_BTN = 4                            # кнопка між піном і землею (ESP32: GPIO4)

FLASH_MS = 200                         # тривалість кожної півфази (горить / згас)

led = Pin(PIN_LED, Pin.OUT)
btn = Pin(PIN_BTN, Pin.IN, Pin.PULL_UP)  # у спокої 1; натиск замикає на землю → 0
led.value(0)

flashes_left = 0                       # скільки перемикань стану ще лишилось
led_on       = False
last_change  = time.ticks_ms()

def start_burst(n):
    global flashes_left, last_change, led_on
    flashes_left = n * 2               # n спалахів = 2·n змін стану
    last_change  = time.ticks_ms()
    led_on       = True                # перше перемикання — одразу вмикаємо
    led.value(1)

was_pressed = False
while True:
    now = time.ticks_ms()

    # 1) подія: натиск запускає пачку, лише коли попередня вже добігла
    pressed = (btn.value() == 0)
    if pressed and not was_pressed and flashes_left == 0:
        start_burst(3)                 # блимнути тричі
    was_pressed = pressed

    # 2) сам неблокуючий прогін пачки
    if flashes_left > 0 and time.ticks_diff(now, last_change) >= FLASH_MS:
        last_change = now
        flashes_left -= 1
        if flashes_left == 0:
            led_on = False             # остання фаза — гарантовано гасимо
        else:
            led_on = not led_on
        led.value(1 if led_on else 0)
