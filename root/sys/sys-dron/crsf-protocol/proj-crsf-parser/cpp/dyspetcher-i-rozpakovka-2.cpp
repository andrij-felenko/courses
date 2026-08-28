// 22 байти → 16 каналів по 11 біт, little-endian.
static void crsf_unpack_channels(const uint8_t *p) {
    uint32_t acc = 0;   // накопичувач бітів
    uint8_t  bits = 0;  // скільки валідних бітів зараз в acc
    uint8_t  ch = 0;    // індекс каналу
    for (uint8_t i = 0; i < 22 && ch < 16; ++i) {
        acc |= (uint32_t)p[i] << bits;   // доливаємо байт зверху
        bits += 8;
        while (bits >= 11 && ch < 16) {  // зчерпуємо всі готові канали
            g_channels[ch++] = (uint16_t)(acc & 0x7FF); // нижні 11 біт
            acc >>= 11;
            bits -= 11;
        }
    }
}
