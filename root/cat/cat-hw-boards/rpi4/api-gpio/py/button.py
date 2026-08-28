# button.py — читаємо кнопку на GPIO27 з внутрішньою підтяжкою до плюса.
# Кнопка: один контакт на GPIO27, другий на GND. Натиснуто = 0, відпущено = 1.
# Прив'язка gpiod v2 на Python.
import time
import gpiod
from gpiod.line import Direction, Bias, Value

from blink import open_header_chip   # ту саму функцію пошуку чипа беремо з blink.py

BTN_OFFSET = 27        # GPIO27 = фізичний штир 13


def main():
    path = open_header_chip()
    if path is None:
        print("немає контролера гребінки")
        return 1

    # Запит: вхід + внутрішня підтяжка до плюса (PULL_UP).
    with gpiod.request_lines(
        path,
        consumer="button",
        config={
            BTN_OFFSET: gpiod.LineSettings(
                direction=Direction.INPUT,
                bias=Bias.PULL_UP,
            )
        },
    ) as request:
        # Опитуємо кнопку й друкуємо лише ЗМІНИ стану (щоб не залити термінал).
        prev = Value.ACTIVE   # відпущено на старті
        while True:
            v = request.get_value(BTN_OFFSET)
            if v != prev:
                # ACTIVE = високий = 3.3 В = відпущено; INACTIVE = 0 = натиснуто.
                print("натиснуто" if v == Value.INACTIVE else "відпущено")
                prev = v
            time.sleep(0.005)   # опитувати раз на 5 мс


if __name__ == "__main__":
    raise SystemExit(main())
