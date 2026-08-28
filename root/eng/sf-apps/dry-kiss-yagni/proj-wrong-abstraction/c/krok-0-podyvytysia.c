// --- ДО: клубок. Один прохід, розгалуження на кожен прапорець. ---
void send_frame(const uint8_t *payload, size_t len,
                bool with_crc, bool compress, bool big_endian) {
    uint8_t body[256];
    size_t  n;

    // 1) тіло: стиснути чи скопіювати як є
    if (compress) {
        n = rle_compress(payload, len, body);       // стиснення RLE
    } else {
        n = len;
        memcpy(body, payload, len);
    }

    // 2) порядок байтів: за прапорцем — перевернути
    if (big_endian) {
        for (size_t i = 0; i < n / 2; i++) {
            uint8_t t = body[i];
            body[i] = body[n - 1 - i];
            body[n - 1 - i] = t;
        }
    }

    // 3) конверт + опційний CRC, усе намішано разом
    uint8_t frame[300];
    size_t  f = 0;
    frame[f++] = 0xAA;                 // старт
    frame[f++] = (uint8_t)n;           // довжина тіла
    memcpy(frame + f, body, n); f += n;
    if (with_crc) {
        frame[f++] = crc8(body, n);    // CRC саме тіла
    }
    frame[f++] = 0x55;                 // стоп

    hw_tx(frame, f);
}
