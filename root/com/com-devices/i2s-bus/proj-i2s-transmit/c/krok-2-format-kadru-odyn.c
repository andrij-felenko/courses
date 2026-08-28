// Формати, які вміє периферія. Значення — умовні коди регістра режиму.
#define I2S_FMT_PHILIPS   0   // «справжній» I2S: MSB через 1 такт після WS
#define I2S_FMT_LEFT_J    1   // left-justified: MSB одразу з фронтом WS
#define I2S_FMT_RIGHT_J   2   // right-justified: LSB притиснутий до кінця слота

void i2s_tx_set_format(uint8_t fmt, uint8_t bits, uint8_t channels) {
    uint32_t conf = 0;

    // Головний перемикач: де в слоті лежить слово. Одна помилка тут = шум.
    conf |= (fmt & 0x3) << TX_FORMAT_SHIFT;

    // Розрядність слова в слоті. Мусить дорівнювати очікуваній приймачем.
    conf |= (bits_code(bits)) << TX_BITS_SHIFT;

    // Стерео: два слова на кадр (лівий, тоді правий).
    if (channels == 2) conf |= TX_STEREO;

    // Порядок бітів: старшим уперед (MSB-first) — так вимагає I2S.
    conf |= TX_MSB_FIRST;

    I2S_TX_CONF = conf;
}
