# button.py — читаємо кнопку на GPIO 27 із внутрішньою підтяжкою до плюса
# постановка:  sudo apt install python3-libgpiod   (пакет gpiod)
import time
import gpiod
from gpiod.line import Direction, Bias, Value

CHIP_PATH = "/dev/gpiochip0"
BTN_LINE  = 27

with gpiod.request_lines(
    CHIP_PATH,
    consumer="button",
    config={
        BTN_LINE: gpiod.LineSettings(
            direction=Direction.INPUT,
            # внутрішня підтяжка до 3.3 В: у спокої лінія читається як ACTIVE
            bias=Bias.PULL_UP,
        )
    },
) as req:
    print("натисніть кнопку (Ctrl+C — вихід)")
    prev = None
    while True:
        v = req.get_value(BTN_LINE)
        # ПІДТЯЖКА ДО ПЛЮСА: ACTIVE (=3.3 В) — відпущено, INACTIVE (=0) — натиснуто
        pressed = (v == Value.INACTIVE)
        if pressed != prev:                # друкуємо лише коли стан змінився
            print("натиснуто" if pressed else "відпущено")
            prev = pressed
        time.sleep(0.02)                   # 20 мс — заразом гасить дребезг
