# blink.py — блимаємо світлодіодом на GPIO 17 через libgpiod v2
# постановка:  sudo apt install python3-libgpiod   (пакет gpiod)
import time
import gpiod
from gpiod.line import Direction, Value

CHIP_PATH = "/dev/gpiochip0"   # гребінка на Pi 5 у свіжому ядрі
LED_LINE  = 17                 # BCM-зсув, а НЕ фізичний штирок

# request_lines бере той самий набір понять, що й C: зсув лінії, її
# налаштування (напрямок, старт) і підпис споживача. Менеджер контексту
# (with) сам звільнить лінію й закриє чип на виході — це заміна кроку 6.
with gpiod.request_lines(
    CHIP_PATH,
    consumer="blink",
    config={
        LED_LINE: gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.INACTIVE,   # старт — низький рівень
        )
    },
) as req:
    # блимаємо: ACTIVE → горить, INACTIVE → згас, пауза 500 мс
    for _ in range(20):
        req.set_value(LED_LINE, Value.ACTIVE)
        time.sleep(0.5)
        req.set_value(LED_LINE, Value.INACTIVE)
        time.sleep(0.5)
