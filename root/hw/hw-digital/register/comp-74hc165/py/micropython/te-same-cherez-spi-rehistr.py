from machine import Pin, SPI
from time import sleep_us

# CP → SCK,  Q7 → MISO (апаратні виводи SPI).
# PL лишається звичайним GPIO (защіпка).
pl = Pin(5, Pin.OUT)
# Режим SPI: polarity=0, phase=0 (вибірка по фронту 0→1, як любить 165).
spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0)

def hc165_read_spi():
    # 1. Защіпнути входи імпульсом PL=0 (так само, як у bit-bang).
    pl.value(0)
    sleep_us(1)
    pl.value(1)

    # 2. Один обмін по SPI: висуваємо «сміття», приймаємо 8 бітів з Q7.
    return spi.read(1, 0x00)[0]   # повертає прийнятий байт
