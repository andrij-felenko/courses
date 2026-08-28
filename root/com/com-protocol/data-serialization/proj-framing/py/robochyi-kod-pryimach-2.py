# Мінімальний CRC-16/CCITT (поліном 0x1021) — для прикладу побайтово.
# У прошивці частіше беруть табличний варіант заради швидкості.
def crc16_ccitt(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF                 # тримаємо 16 біт (Python-int безмежний)
    return crc

# сюди приймач кладе те, що робити з валідним кадром
def handle_frame(data):
    ...

# метод класу FrameRx з попередньої вкладки
def _complete(self):
    if len(self.buf) < 3:                # кадр коротший за 1 байт даних + 2 CRC — брак
        return

    body = len(self.buf) - 2             # тіло без двох байтів CRC
    got  = (self.buf[body] << 8) | self.buf[body + 1]  # CRC із кадру (big-endian)
    calc = crc16_ccitt(self.buf[:body])                # рахуємо самі

    if got == calc:                      # сума зійшлася — кадр цілий
        handle_frame(bytes(self.buf[:body]))  # віддаємо тіло логіці
    # не зійшлася — тихо відкидаємо: приймач уже в WAIT, чекає наступного FLAG
