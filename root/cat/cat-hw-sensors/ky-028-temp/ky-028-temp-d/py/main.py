from machine import Pin
from time import sleep_ms

do_pin = Pin(4, Pin.IN)          # цифровий вихід модуля (поріг)
led    = Pin(2, Pin.OUT)         # вбудований світлодіод плати
was_hot = False                  # попередній стан, щоб ловити саме ПЕРЕХІД

while True:
    # на типовій платі: спокій = 1, перетин порогу тягне DO в 0.
    # ЯКЩО твоя партія навпаки — заміни 0 на 1 у цьому рядку:
    hot = (do_pin.value() == 0)

    led.value(1 if hot else 0)   # світимо, поки «гаряче»

    if hot != was_hot:           # друкуємо тільки момент перемикання
        print("перетнуло поріг: ГАРЯЧЕ" if hot else "нижче порогу: норма")
        was_hot = hot
    sleep_ms(20)
