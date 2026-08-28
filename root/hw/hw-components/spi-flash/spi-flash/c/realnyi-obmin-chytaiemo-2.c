// Перед КОЖНИМ записом чи стиранням флеш вимагає окремий дозвіл:
// засувка дозволу сама скидається після кожної операції.
void flash_write_enable(void) {
    cs_low();
    spi_xfer(0x06);                 // WRITE ENABLE
    cs_high();
}

// Пишемо до однієї сторінки. len не має перетинати межу сторінки (256 Б):
// інакше адреса «загорнеться» на початок тієї ж сторінки й затре початок.
void flash_page_program(uint32_t addr, const uint8_t *data, uint32_t len) {
    flash_write_enable();           // без цього запис мовчки не відбудеться
    cs_low();
    spi_xfer(0x02);                 // опкод PAGE PROGRAM
    spi_xfer((addr >> 16) & 0xFF);
    spi_xfer((addr >> 8)  & 0xFF);
    spi_xfer(addr & 0xFF);
    for (uint32_t i = 0; i < len; i++)
        spi_xfer(data[i]);          // байти течуть у флеш
    cs_high();                      // підняли вибір — флеш ПОЧИНАЄ писати
    flash_wait_busy();              // і поки пише, вона зайнята — треба зачекати
}
