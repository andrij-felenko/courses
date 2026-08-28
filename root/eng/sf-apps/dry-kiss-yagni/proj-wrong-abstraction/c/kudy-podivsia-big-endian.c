// Формат "be": перевернуте тіло + CRC перевернутого тіла.
// Це НЕ поперечний прапорець, а окремий формат — тому окрема функція.
void send_be(const uint8_t *payload, size_t len) {
    uint8_t body[256];
    size_t  n = len;
    for (size_t i = 0; i < len; i++)     // копія з переворотом
        body[i] = payload[len - 1 - i];

    uint8_t frame[300];
    size_t  f = envelope_begin(frame, body, n);
    frame[f++] = crc8(body, n);          // CRC саме перевернутого тіла
    frame[f++] = 0x55;
    hw_tx(frame, f);
}
