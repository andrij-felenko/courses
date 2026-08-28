uint8_t spi_transfer(uint8_t out);        // один байт туди-назад по SPI
void    spi_set_hz(uint32_t hz);          // змінити частоту такту
void    cs_low(void);  void cs_high(void);// смикнути лінію вибору чипа (NCS)

// Запис регістра: старший біт = 0. Завжди на 1 МГц.
void spi_write_reg(uint8_t reg, uint8_t val) {
    spi_set_hz(1000000);                  // конфіг — не швидше 1 МГц!
    cs_low();
    spi_transfer(reg & 0x7F);             // біт 7 = 0 → запис
    spi_transfer(val);
    cs_high();
}

// Читання n регістрів: старший біт = 1. Дані можна на 20 МГц.
void spi_read_regs(uint8_t reg, uint8_t *buf, uint8_t n) {
    spi_set_hz(20000000);                 // дані — до 20 МГц
    cs_low();
    spi_transfer(reg | 0x80);             // біт 7 = 1 → читання
    for (uint8_t i = 0; i < n; i++)
        buf[i] = spi_transfer(0x00);      // тактуємо нулями, приймаємо байти
    cs_high();
}
