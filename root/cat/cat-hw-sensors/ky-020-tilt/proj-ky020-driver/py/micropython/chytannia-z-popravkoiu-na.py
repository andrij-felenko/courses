from machine import Pin
import time

TILT = 2                                # пін S давача

# підтяжка вже на модулі; PULL_UP теж годиться, гірше не буде
tilt = Pin(TILT, Pin.IN, Pin.PULL_UP)

def is_tilted():
    # Уся інверсія — ТУТ, і більше ніде. 0 = кулька сіла на землю = нахил.
    return tilt.value() == 0

while True:
    print("нахил" if is_tilted() else "рівно")
    time.sleep_ms(200)
