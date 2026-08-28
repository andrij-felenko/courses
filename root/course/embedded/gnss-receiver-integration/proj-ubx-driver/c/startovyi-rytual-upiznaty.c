// Зовнішня функція платформи: віддати n байтів у UART модуля.
extern void uart_write(const uint8_t *data, uint16_t n);

// Скласти UBX-пакет (сигнатура, class/id, len, payload, сума) і відіслати.
static void ubx_send(uint8_t cls, uint8_t id, const uint8_t *payload, uint16_t len) {
    uint8_t hdr[6] = { UBX_SYNC1, UBX_SYNC2, cls, id,
                       (uint8_t)(len & 0xFF), (uint8_t)(len >> 8) };
    // Сума Флетчера — від class (hdr[2]) до кінця payload.
    uint8_t a = 0, b = 0;
    for (int i = 2; i < 6; i++) { a += hdr[i]; b += a; }
    for (uint16_t i = 0; i < len; i++) { a += payload[i]; b += a; }

    uart_write(hdr, 6);
    if (len) uart_write(payload, len);
    uint8_t ck[2] = { a, b };
    uart_write(ck, 2);
}
