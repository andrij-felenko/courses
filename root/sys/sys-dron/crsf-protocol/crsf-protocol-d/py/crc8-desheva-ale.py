# CRC8/DVB-S2, поліном 0xD5. Рахуємо по байтах: тип + дані.
def crsf_crc8(ptr):
    crc = 0
    for byte in ptr:
        crc ^= byte                          # вкидаємо черговий байт
        for _ in range(8):                   # прокручуємо 8 бітів
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc

# Перевірка цілого кадру:
#   frame[0] = 0xC8 (старт), frame[1] = len, далі тип+дані, останній = CRC
def crsf_frame_ok(frame):
    length = frame[1]                        # тип + дані + CRC
    got = frame[2 + length - 1]              # останній байт = присланий CRC
    calc = crsf_crc8(frame[2:2 + length - 1])  # від типу до кінця даних
    return got == calc
