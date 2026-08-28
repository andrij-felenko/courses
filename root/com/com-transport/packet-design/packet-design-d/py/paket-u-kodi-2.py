# Перевірити кадр. Повертає (id, data) для цілого кадру або None.
def check(buf: bytes):
    if len(buf) < 4 or buf[0] != SYNC:            # нема SYNC або замало байтів
        return None
    L = buf[1]                                     # LEN = ID + дані
    if L + 3 != len(buf):                          # довжина не збігається з кадром
        return None
    if crc8(buf[1:2 + L]) != buf[-1]:              # CRC не зійшовся
        return None
    return buf[2], buf[3:2 + L]                    # (id, самі дані без ID)
