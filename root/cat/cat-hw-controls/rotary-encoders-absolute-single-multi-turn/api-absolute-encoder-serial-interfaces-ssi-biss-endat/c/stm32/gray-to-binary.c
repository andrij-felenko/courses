// Приклад декодування кадру SSI (25 біт) та перетворення коду Грея в двійковий на C
#include <stdint.h>

uint32_t gray_to_binary(uint32_t gray) {
    uint32_t binary = gray;
    while (gray >>= 1) {
        binary ^= gray;
    }
    return binary;
}

uint32_t parse_ssi_frame(uint8_t* spi_buffer) {
    // Збирання 32-бітного слова з трьох байтів SPI
    uint32_t raw_data = ((uint32_t)spi_buffer[0] << 16) |
                        ((uint32_t)spi_buffer[1] << 8)  |
                         (uint32_t)spi_buffer[2];
    
    // Виділення 24-бітного поля позиції (зсув 1 біт праворуч)
    uint32_t gray_position = (raw_data >> 1) & 0x00FFFFFF;
    
    // Перетворення коду Грея в двійковий формат
    return gray_to_binary(gray_position);
}
