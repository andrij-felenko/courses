from machine import UART, Pin
import time

uart = UART(2, baudrate=9600, bits=8, parity=None, stop=1, rx=16, tx=17)
time.sleep_ms(30)
uart.write("s5-1#")            # перемкнути модуль у пасивний режим
time.sleep_ms(30)              # дати час перетравити й відповісти "ok"
uart.read()                    # прибрати "ok" з буфера

def tof_query():
    """Запитати відстань один раз. Повертає мм або None."""
    uart.read()                                   # чистимо старе
    uart.write("r6#")                             # «дай відстань зараз»

    # Відповідь виду "L=748\r\n" — беремо цифри після '='
    buf = bytearray(); seen_eq = False
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < 100:   # чекаємо до 100 мс
        c = uart.read(1)
        if c is None:
            continue
        if c == b'=':
            seen_eq = True
            continue
        if seen_eq and b'0' <= c <= b'9':
            buf += c
        elif seen_eq and c in (b'\r', b'\n'):
            break                                 # рядок скінчився
    if not buf:
        return None
    return int(buf)
