from machine import Pin
import time

PIN_LED = 5                            # S модуля на цифровому виході (ESP32: GPIO5)

ON_MS  = 500                           # скільки триває «увімкнено»
OFF_MS = 500                           # скільки триває «згасло»

led = Pin(PIN_LED, Pin.OUT)
led.value(0)                           # старт зі згаслого — відомий початковий стан

led_on = False
last_change = time.ticks_ms()          # коли востаннє перемикали

while True:
    now = time.ticks_ms()
    phase = ON_MS if led_on else OFF_MS
    # ticks_diff коректно рахує різницю навіть на переповненні лічильника
    if time.ticks_diff(now, last_change) >= phase:
        last_change = now
        led_on = not led_on
        led.value(1 if led_on else 0)

    # тут цикл пролітає вільно — можна читати давачі, крутити іншу логіку
