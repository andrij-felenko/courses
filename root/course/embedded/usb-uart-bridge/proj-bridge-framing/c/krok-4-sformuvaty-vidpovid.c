// Зібрати кадр [SYNC][LEN][дані…][CRC] у out і відправити в UART (до моста, далі на ПК).
// out має вмістити len + 3 байти.
void frame_send(const uint8_t *data, uint8_t len) {
    uint8_t out[MAX_PAYLOAD + 3];
    if (len > MAX_PAYLOAD) return;          // не відсилаємо те, що не влазить у формат

    out[0] = FRAME_SYNC;
    out[1] = len;
    uint8_t crc = crc8_step(0x00, len);     // CRC: спершу LEN
    for (uint8_t i = 0; i < len; i++) {
        out[2 + i] = data[i];
        crc = crc8_step(crc, data[i]);      // потім кожен байт даних
    }
    out[2 + len] = crc;

    uart_write_buf(out, (size_t)(len + 3)); // віддати міст у бік ПК
}
