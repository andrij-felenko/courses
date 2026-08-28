from machine import Pin
import time

do  = Pin(2, Pin.IN)             # цифровий вихід KY-026, поріг задано гвинтиком
led = Pin(25, Pin.OUT)           # вбудований світлодіод плати

while True:
    # 0 = поріг перейдено = є вогонь;  1 = вогню немає (для інвертованого DO)
    flame = do.value() == 0
    led.value(1 if flame else 0)
    print("ВОГОНЬ" if flame else "спокійно")
    time.sleep_ms(50)
