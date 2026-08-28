from machine import ADC, Pin
from time import sleep_ms

vrx = ADC(Pin(34))                     # VRx на аналоговому вході
vry = ADC(Pin(35))                     # VRy на аналоговому вході
sw  = Pin(32, Pin.IN, Pin.PULL_UP)     # КЛЮЧОВЕ: на модулі підтяжки немає

while True:
    x = vrx.read()                     # 0..4095: центр ≈ 2048
    y = vry.read()                     # 0..4095: центр ≈ 2048
    pressed = (sw.value() == 0)        # натиск = 0 (підтяжка!)

    print("X={} Y={} SW={}".format(x, y, "натиснуто" if pressed else "-"))
    sleep_ms(500)
