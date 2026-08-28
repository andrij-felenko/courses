# ESP32: UART2 — апаратний. Виводи RX2=16, TX2=17 (типові).
# Модуль шле текст на 9600 8N1; його TX іде на RX2 плати.
from machine import UART, Pin

uart = UART(2, baudrate=9600, bits=8, parity=None, stop=1,
            rx=16, tx=17)                        # порт до давача: 9600!

buf = bytearray()          # накопичувач цифр
last_distance = -1

while True:
    if not uart.any():
        continue
    c = uart.read(1)                             # один байт
    if c is None:
        continue
    if b'0' <= c <= b'9':                        # цифра — накопичуємо
        buf += c
    elif c == b'\n':                             # кінець рядка — рядок готовий
        if buf:
            last_distance = int(buf)             # текст → число
            buf = bytearray()                    # буфер під наступний рядок
            print(last_distance, "mm")
    # 'm', '\r', пробіл, будь-що інше — ігноруємо
