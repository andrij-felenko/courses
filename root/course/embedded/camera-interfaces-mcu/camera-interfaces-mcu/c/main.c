// Регістри буфера-контролера (умовні, як у поширених SPI-камер):
#define REG_CAPTURE     0x84  // біт[1]=1 → почати захоплення кадру
#define REG_STATUS      0x41  // біт[3] → кадр знято й лежить у буфері
#define REG_FIFO_READ   0x3D  // потоково читати байти кадру
#define STATUS_DONE_BIT (1 << 3)

void camera_take_frame(uint8_t *dst, uint32_t len) {
    spi_write_reg(REG_CAPTURE, 0x02);        // старт: біт[1]=1

    // Чекаємо, поки буфер сам складе весь кадр — МК тут вільний,
    // потік від сенсора ловить буфер, а не ми.
    while (!(spi_read_reg(REG_STATUS) & STATUS_DONE_BIT)) {
        /* можна робити інші справи або просто чекати */
    }

    // Кадр готовий і нікуди не дінеться — читаємо його НЕСПІШНО,
    // байт за байтом, зі швидкістю, яку тягне наш SPI.
    spi_cs_low();
    spi_transfer(REG_FIFO_READ);             // команда «віддавай FIFO»
    for (uint32_t i = 0; i < len; i++)
        dst[i] = spi_transfer(0x00);         // тактуємо — буфер віддає наступний байт
    spi_cs_high();
}
