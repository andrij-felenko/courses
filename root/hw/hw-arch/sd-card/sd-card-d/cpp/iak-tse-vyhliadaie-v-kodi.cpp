// SPI-режим SD: послати команду (6 байтів) і дочекатися байта-відповіді R1.
// spi_xchg(b) — обміняти один байт по SPI; CS_LOW/CS_HIGH — лінія вибору картки.
static uint8_t sd_cmd(uint8_t cmd, uint32_t arg, uint8_t crc) {
    spi_xchg(0xFF);                       // такт «вхолосту» перед командою
    spi_xchg(0x40 | cmd);                 // стартові біти + номер команди
    spi_xchg(arg >> 24); spi_xchg(arg >> 16);
    spi_xchg(arg >> 8);  spi_xchg(arg);   // 4 байти аргументу, старший першим
    spi_xchg(crc | 0x01);                 // CRC потрібен лише для CMD0/CMD8
    for (int i = 0; i < 8; i++) {         // відповідь приходить за кілька тактів
        uint8_t r = spi_xchg(0xFF);
        if ((r & 0x80) == 0) return r;    // старший біт 0 -> це валідна R1
    }
    return 0xFF;                          // картка не відповіла
}

// Розбудити картку й перевести її в SPI-режим. Повертає 0, якщо вдалося.
int sd_init(void) {
    spi_set_clock_slow();                 // 100-400 кГц на час ініціалізації
    CS_HIGH();
    for (int i = 0; i < 10; i++) spi_xchg(0xFF);   // >= 74 тактів, CS високий

    CS_LOW();
    if (sd_cmd(0, 0x00000000, 0x94) != 0x01) { CS_HIGH(); return -1; } // CMD0: idle
    sd_cmd(8, 0x000001AA, 0x86);          // CMD8: перевірка діапазону живлення (+ 4 байти R7)
    for (int i = 0; i < 4; i++) spi_xchg(0xFF);

    for (int tries = 0; tries < 1000; tries++) {   // ACMD41 у циклі — чекаємо готовності
        sd_cmd(55, 0, 0xFF);              // ACMD = CMD55, потім сама команда
        if (sd_cmd(41, 0x40000000, 0xFF) == 0x00) { // біт HCS=1 (підтримка SDHC)
            CS_HIGH();
            spi_set_clock_fast();         // готово -> можна на повну частоту
            return 0;
        }
    }
    CS_HIGH();
    return -1;                            // картка так і не вийшла з idle
}
