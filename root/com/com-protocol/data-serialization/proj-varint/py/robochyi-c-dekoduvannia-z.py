# Повертає (значення, число_зчитаних_байтів); (None, 0) при помилці.
def varint_decode_u32(buf: bytes):
    result = 0
    shift = 0
    for i, b in enumerate(buf):
        # Наростити результат: молодші 7 бітів цього байта на позицію shift.
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:              # старший біт 0 → це останній байт числа
            return result & 0xFFFFFFFF, i + 1  # успіх
        shift += 7
        if shift >= 32:                  # задовгий varint для 32 бітів → потік зіпсовано
            return None, 0
    return None, 0                       # прапорець ще «далі є», а буфер скінчився → обірвано
