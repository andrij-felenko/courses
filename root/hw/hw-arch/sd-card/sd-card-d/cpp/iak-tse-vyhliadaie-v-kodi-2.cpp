// Прочитати один 512-байтовий сектор у buf. lba — номер сектора.
// Для SDHC/SDXC адреса = номер сектора; для старих SDSC було б lba*512.
int sd_read_block(uint32_t lba, uint8_t *buf) {
    CS_LOW();
    if (sd_cmd(17, lba, 0xFF) != 0x00) { CS_HIGH(); return -1; }  // CMD17: read single block
    uint8_t token;                        // чекаємо маркер початку даних
    do { token = spi_xchg(0xFF); } while (token == 0xFF);
    if (token != 0xFE) { CS_HIGH(); return -2; }                  // 0xFE = дані пішли
    for (int i = 0; i < 512; i++) buf[i] = spi_xchg(0xFF);        // рівно 512 байтів
    spi_xchg(0xFF); spi_xchg(0xFF);       // два байти CRC -> у SPI відкидаємо
    CS_HIGH();
    return 0;                             // сектор у buf
}
