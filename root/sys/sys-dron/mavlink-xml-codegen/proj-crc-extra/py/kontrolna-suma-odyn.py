POLY = 0x8408          # дзеркальне подання твірного многочлена 0x1021
INIT = 0xFFFF

def crc16_bitwise(data, crc=INIT):
    """CRC-16/MCRF4XX побітно: вісім кроків на кожен байт."""
    for byte in data:
        crc ^= byte                       # байт заходить у молодші вісім бітів
        for _ in range(8):
            if crc & 1:                   # вилітлий біт = 1 → домішуємо многочлен
                crc = (crc >> 1) ^ POLY
            else:
                crc >>= 1
    return crc
