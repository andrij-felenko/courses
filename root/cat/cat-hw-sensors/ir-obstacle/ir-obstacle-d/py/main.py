from machine import Pin
import time

# цифровий вихід давача (FC-51 OUT або KY-032 OUT); підтяжка на випадок «плаваючої» лінії
pin_out = Pin(2, Pin.IN, Pin.PULL_UP)
led = Pin(13, Pin.OUT)             # вбудований світлодіод

while True:
    # 0 = перешкода є (активний нуль);  1 = вільно
    obstacle = pin_out.value() == 0
    led.value(1 if obstacle else 0)
    print("ПЕРЕШКОДА" if obstacle else "вільно")
    time.sleep_ms(30)
