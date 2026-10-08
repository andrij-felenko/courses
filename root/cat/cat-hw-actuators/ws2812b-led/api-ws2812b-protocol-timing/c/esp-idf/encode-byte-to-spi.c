#include "driver/spi_master.h"
#include "esp_err.h"

// Формування бітового масиву для одного колірного байта WS2812B через SPI (2.4 МГц)
// Кожен біт WS2812B розгортається у 3 біти SPI: '0' -> 0b100, '1' -> 0b110
void encode_byte_to_spi(uint8_t byte_val, uint8_t *out_spi_buf) {
    uint32_t spi_pattern = 0;
    for (int i = 7; i >= 0; i--) {
        spi_pattern <<= 3;
        if (byte_val & (1 << i)) {
            spi_pattern |= 0b110; // Біт 1 WS2812B
        } else {
            spi_pattern |= 0b100; // Біт 0 WS2812B
        }
    }
    // Запис 24 бітів SPI (3 байти) у вихідний буфер DMA
    out_spi_buf[0] = (uint8_t)(spi_pattern >> 16);
    out_spi_buf[1] = (uint8_t)(spi_pattern >> 8);
    out_spi_buf[2] = (uint8_t)(spi_pattern);
}
