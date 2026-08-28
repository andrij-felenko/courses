#include <stdint.h>

// Адресу розкладаємо старшим байтом уперед — саме такого порядку чекає флеш.
void flash_read(uint32_t addr, uint8_t *buf, uint32_t len) {
    cs_low();                       // опустили вибір чипа — відкрили розмову
    spi_xfer(0x03);                 // опкод READ
    spi_xfer((addr >> 16) & 0xFF);  // адреса: старший байт A23..16
    spi_xfer((addr >> 8)  & 0xFF);  // середній байт A15..8
    spi_xfer(addr & 0xFF);          // молодший байт A7..0
    for (uint32_t i = 0; i < len; i++)
        buf[i] = spi_xfer(0x00);    // штовхаємо пустушку, читаємо байт у відповідь
    cs_high();                      // підняли вибір — закрили розмову
}
