# blink.py — блимаємо світлодіодом на GPIO17. Прив'язка gpiod v2 на Python.
# Встановити:  sudo apt install python3-libgpiod   (або: pip install gpiod)
import glob
import time
import gpiod
from gpiod.line import Direction, Value

LED_OFFSET = 17        # GPIO17 = фізичний штир 11 (номер BCM, не штир!)


def open_header_chip():
    # Знайти символьний пристрій контролера гребінки за міткою pinctrl-*.
    # Повертає шлях /dev/gpiochipN або None — код не залежить від номера чипа.
    for path in sorted(glob.glob("/dev/gpiochip*")):
        with gpiod.Chip(path) as chip:
            # Контролер гребінки має мітку pinctrl-* (bcm2711 на Pi4, rp1 на Pi5).
            if chip.get_info().label.startswith("pinctrl"):
                return path
    return None


def main():
    path = open_header_chip()
    if path is None:
        print("не знайшов контролер гребінки (pinctrl-*)")
        return 1

    # Запит на володіння: напрям — вихід, старт із нуля (згашено),
    # мітка-ім'я "blink" (її покаже gpioinfo). Одна дія замість набору об'єктів C.
    with gpiod.request_lines(
        path,
        consumer="blink",
        config={
            LED_OFFSET: gpiod.LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.INACTIVE,
            )
        },
    ) as request:
        # Блимаємо: 10 разів, по 0.5 с у кожному стані.
        for _ in range(10):
            request.set_value(LED_OFFSET, Value.ACTIVE)
            time.sleep(0.5)
            request.set_value(LED_OFFSET, Value.INACTIVE)
            time.sleep(0.5)
    # Вихід із `with` сам звільняє лінію (ядро зробило б це й само при виході).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
