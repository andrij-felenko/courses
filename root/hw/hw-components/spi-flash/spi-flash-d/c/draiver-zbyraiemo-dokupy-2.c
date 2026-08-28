// Повертає 24-бітний ідентифікатор: [виробник][модель_старша][модель_молодша].
uint32_t flash_read_jedec_id(void) {
    cs_low();
    spi_xfer(0x9F);                 // READ JEDEC ID
    uint8_t mf  = spi_xfer(0x00);   // байт виробника
    uint8_t th  = spi_xfer(0x00);   // старший байт моделі
    uint8_t tl  = spi_xfer(0x00);   // молодший байт моделі
    cs_high();
    return ((uint32_t)mf << 16) | ((uint32_t)th << 8) | tl;
}
