from machine import UART, Pin

# 9600 8N1, апаратний порт; ніжки tx/rx — під свою плату.
uart = UART(1, baudrate=9600, tx=Pin(17), rx=Pin(16))

_buf = bytearray()

# Кладемо цифри в буфер; на кінці рядка віддаємо готове число.
# Повертає >=0, коли надійшло ЦІЛЕ нове число; None, якщо рядок ще не завершено.
def tof_poll_uart():
    global _buf
    while uart.any():                      # апаратний порт ловить байти у фоні
        c = uart.read(1)
        if b'0' <= c <= b'9':              # цифра → накопичуємо
            if len(_buf) < 7:
                _buf += c
        elif c == b'\n':                   # кінець рядка → число готове
            mm = int(_buf) if _buf else -1
            _buf = bytearray()             # чистимо буфер під наступне число
            if mm >= 0:
                return mm
        # усе інше (b'm', b'\r', пробіли, сміття) — просто пропускаємо
    return None                            # цілого рядка ще нема

while True:
    mm = tof_poll_uart()
    if mm is not None:
        print(mm, "мм")
    # цикл не блокується — тут може крутитися будь-яка інша робота
