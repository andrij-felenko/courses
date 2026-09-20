// Перетворення 32-бітного коду Ґрея у двійковий код
uint32_t encoder_gray_to_binary(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}

// Розрахунок 6-бітного CRC для протоколу BiSS-C (поліном P(x) = x^6 + x + 1)
uint8_t encoder_calc_crc6(uint64_t frame_data, uint8_t bit_len) {
    uint8_t crc = 0x00;
    for (int8_t i = bit_len - 1; i >= 0; i--) {
        bool bit = (frame_data >> i) & 1;
        bool crc_msb = (crc >> 5) & 1;
        crc = (crc << 1) & 0x3F;
        if (bit ^ crc_msb) {
            crc ^= 0x03; // Маска полінома x^6 + x + 1 без старшого біта
        }
    }
    return crc ^ 0x3F; // Інверсія залишку
}
