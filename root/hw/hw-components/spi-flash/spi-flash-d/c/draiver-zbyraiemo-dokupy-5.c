// Пишемо до однієї сторінки. len ≤ скільки лишилося до кінця сторінки.
void flash_page_program(uint32_t addr, const uint8_t *data, uint32_t len) {
    flash_write_enable();
    cs_low();
    spi_xfer(0x02);                 // PAGE PROGRAM
    spi_xfer((addr >> 16) & 0xFF);
    spi_xfer((addr >> 8)  & 0xFF);
    spi_xfer(addr & 0xFF);
    for (uint32_t i = 0; i < len; i++)
        spi_xfer(data[i]);          // байти течуть у флеш
    cs_high();                      // підняли вибір — чип ПОЧИНАЄ писати
    flash_wait_busy();              // поки пише — зайнятий, чекаємо
}
