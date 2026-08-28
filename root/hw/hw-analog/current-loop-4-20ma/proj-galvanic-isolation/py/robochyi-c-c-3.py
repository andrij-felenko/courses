from typing import Callable

def iso_capture_point(adc_read: Callable[[], int], n: int) -> int:
    """
    Захопити одну калібрувальну точку: усереднити N читань АЦП ізолятора.
    adc_read — апаратне читання коду АЦП приймача.
    Викликають двічі: подавши 4 мА, потім 20 мА на вхід ізолятора.
    """
    acc = sum(adc_read() for _ in range(n))
    return acc // n                          # усереднений код точки


def iso_calibrate(c: IsoCal, adc_read: Callable[[], int]) -> None:
    """Повне двоточкове калібрування ізолятора."""
    # Оператор подав на вхід ізолятора рівно 4.000 мА (еталонне джерело).
    c.adc_at_4mA = iso_capture_point(adc_read, 256)

    # Оператор подав рівно 20.000 мА.
    c.adc_at_20mA = iso_capture_point(adc_read, 256)

    # Далі c зберігають у незалежну пам'ять (EEPROM/Flash) —
    # щоб калібрування пережило вимкнення живлення.
