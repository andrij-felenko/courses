void flash_write_enable(void) {
    cs_low();
    spi_xfer(0x06);                 // WRITE ENABLE: підняти засувку дозволу
    cs_high();
}

// Опитуємо регістр статусу (0x05); біт 0 = «запис триває».
void flash_wait_busy(void) {
    cs_low();
    spi_xfer(0x05);                 // READ STATUS REGISTER
    while (spi_xfer(0x00) & 0x01)   // крутимо такт, читаємо статус, поки BUSY = 1
        ;                           // (у бойовому коді тут доречний тайм-аут)
    cs_high();
}
