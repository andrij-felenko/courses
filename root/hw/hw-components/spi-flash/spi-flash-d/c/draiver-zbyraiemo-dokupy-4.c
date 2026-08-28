void flash_sector_erase(uint32_t addr) {
    flash_write_enable();           // без дозволу чип мовчки проігнорує
    cs_low();
    spi_xfer(0x20);                 // SECTOR ERASE (4 КіБ)
    spi_xfer((addr >> 16) & 0xFF);
    spi_xfer((addr >> 8)  & 0xFF);
    spi_xfer(addr & 0xFF);
    cs_high();                      // підняли вибір — чип ПОЧИНАЄ стирати
    flash_wait_busy();              // десятки мілісекунд — чекаємо
}
