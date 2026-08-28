// Контрольна сума UBX (8-бітний Флетчер) над class..payload.
// buf указує на байт class; n — кількість байтів до кінця payload.
void ubx_checksum(const uint8_t *buf, uint16_t n, uint8_t *ck_a, uint8_t *ck_b) {
    uint8_t a = 0, b = 0;
    for (uint16_t i = 0; i < n; i++) {
        a += buf[i];     // накопичує суму байтів
        b += a;          // накопичує суму часткових сум
    }                    // обидва — за модулем 256 (uint8_t переповнюється сам)
    *ck_a = a;
    *ck_b = b;
}
