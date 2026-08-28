#define READ_BIT  0x80     // старший біт адреси: 1 = читання

// Прочитати один регістр: шлемо адресу з READ_BIT, на другому байті
// висуваємо пусте й забираємо вміст регістра.
uint8_t sensor_read_reg(uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(reg | READ_BIT), 0x00 };
    uint8_t rx[2];
    spi_xfer_block(tx, rx, 2);
    return rx[1];          // rx[0] прийшов під час адреси — він нам не потрібен
}

// Записати один регістр: адреса без READ_BIT, тоді байт даних.
void sensor_write_reg(uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { (uint8_t)(reg & ~READ_BIT), val };
    spi_xfer_block(tx, NULL, 2);   // приймати нічого — rx не потрібен
}
