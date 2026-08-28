# blink.py — блимаємо світлодіодом на GPIO17, виведеному платою на макетку
# постановка:  sudo apt install python3-libgpiod   (пакет gpiod)
import time
import gpiod
from gpiod.line import Direction, Value

CHIP_PATH = "/dev/gpiochip0"   # гребінка Pi у свіжому ядрі
LED_LINE  = 17                 # BCM-ім'я, надруковане на платі

# with сам звільнить лінію й закриє чип на виході — заміна release/close
with gpiod.request_lines(
    CHIP_PATH,
    consumer="blink",
    config={LED_LINE: gpiod.LineSettings(direction=Direction.OUTPUT)},
) as req:
    for _ in range(20):
        req.set_value(LED_LINE, Value.ACTIVE)
        time.sleep(0.5)                 # горить 0.5 с
        req.set_value(LED_LINE, Value.INACTIVE)
        time.sleep(0.5)                 # згас 0.5 с
