// Приклад кодування 24-бітного кадру GRB у буфер SPI (ESP-IDF / C)
#include <stdint.h>
#include <stddef.h>

#define WS2812_SPI_BIT_0 0b100 // 1 біт HIGH, 2 біти LOW (416 нс / 833 нс)
#define WS2812_SPI_BIT_1 0b110 // 2 біти HIGH, 1 біт LOW (833 нс / 416 нс)

void encode_pixel_grb(uint8_t g, uint8_t r, uint8_t b, uint8_t *spi_buf) {
    uint32_t grb = ((uint32_t)g << 16) | ((uint32_t)r << 8) | b;
    size_t buf_idx = 0;
    
    for (int8_t bit = 23; bit >= 0; bit--) {
        uint8_t bit_val = (grb >> bit) & 0x01;
        // Кодування кожного біта 3-бітовою послідовністю SPI
        spi_buf[buf_idx++] = bit_val ? WS2812_SPI_BIT_1 : WS2812_SPI_BIT_0;
    }
}
