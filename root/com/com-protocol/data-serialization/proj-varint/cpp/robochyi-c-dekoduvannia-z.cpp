// Розкодувати varint із buf довжиною len у *out.
// Повертає число зчитаних байтів, або 0 при помилці (обірваний або задовгий потік).
size_t varint_decode_u32(const uint8_t *buf, size_t len, uint32_t *out) {
    uint32_t result = 0;
    size_t   i = 0;
    int      shift = 0;

    while (i < len) {
        uint8_t b = buf[i++];
        // Наростити результат: молодші 7 бітів цього байта на позицію shift.
        result |= (uint32_t)(b & 0x7F) << shift;
        if ((b & 0x80) == 0) {           // старший біт 0 → це останній байт числа
            *out = result;
            return i;                    // успіх: повертаємо, скільки байтів з'їли
        }
        shift += 7;
        if (shift >= 32) return 0;        // задовгий varint для 32 бітів → потік зіпсовано
    }
    return 0;                            // дійшли до кінця буфера, а прапорець ще «далі є» → обірвано
}
