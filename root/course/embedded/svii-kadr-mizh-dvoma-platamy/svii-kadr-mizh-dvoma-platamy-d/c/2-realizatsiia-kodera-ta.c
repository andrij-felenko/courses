// Кодування COBS: dst має вміщати щонайменше src_len + (src_len / 254) + 1 байтів
size_t cobs_encode(const uint8_t *src, size_t src_len, uint8_t *dst) {
    if (!src || !dst || src_len == 0) return 0;

    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 1;

    while (read_idx < src_len) {
        if (src[read_idx] == 0x00) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 1;
            read_idx++;
        } else {
            dst[write_idx++] = src[read_idx++];
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 1;
            }
        }
    }
    dst[code_idx] = code;
    return write_idx;
}

// Декодування COBS. Дозволено src == dst (розпакування на місці).
// Повертає довжину відновлених даних або 0 у разі пошкодження структури офсетів.
size_t cobs_decode(const uint8_t *src, size_t src_len, uint8_t *dst) {
    if (!src || !dst || src_len == 0) return 0;

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src_len) {
        uint8_t code = src[read_idx++];
        if (code == 0) return 0; // Помилка: нуль всередині тіла COBS недопустимий

        for (uint8_t i = 1; i < code; ++i) {
            if (read_idx >= src_len) return 0; // Помилка: вихід за межі буфера
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src_len) {
            dst[write_idx++] = 0x00; // Відновлюємо нульовий байт
        }
    }
    return write_idx;
}
