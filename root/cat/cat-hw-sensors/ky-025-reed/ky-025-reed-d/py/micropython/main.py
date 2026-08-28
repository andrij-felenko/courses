from machine import Pin
import time

reed = Pin(2, Pin.IN)      # D0 давача; на платі вже є підтяжка Rp
led  = Pin(13, Pin.OUT)    # вбудований світлодіод

was_near = False           # попередній стан, щоб ловити саме перехід

while True:
    # магніт дає низький рівень → інвертуємо, щоб near=True означало «магніт поруч»
    near = (reed.value() == 0)

    led.value(1 if near else 0)

    if near and not was_near:
        print("магніт піднесено")
    if not near and was_near:
        print("магніт прибрано")
    was_near = near

    time.sleep_ms(20)      # грубе згладжування деренчання контакту
