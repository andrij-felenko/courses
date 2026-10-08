#include <stdint.h>
#include <stdbool.h>

#define AS5048_CMD_READ      0x4000
#define AS5048_REG_ANGLE     0x3FFF
#define AS5048_PARITY_MASK   0x8000
#define AS5048_ERROR_FLAG    0x4000
#define AS5048_DATA_MASK     0x3FFF

// Обчислення парної парності для 16-бітового слова
static bool check_even_parity(uint16_t frame) {
    uint16_t val = frame;
    val ^= val >> 8;
    val ^= val >> 4;
    val ^= val >> 2;
    val ^= val >> 1;
    return (val & 0x1) == 0;
}

bool parse_as5048_spi_frame(uint16_t rx_frame, uint16_t *raw_angle, bool *error_flag) {
    // 1. Перевірка парності кадру
    if (!check_even_parity(rx_frame)) {
        return false; // Помилка цілісності даних на шині SPI
    }
    
    // 2. Перевірка прапорця помилки енкодера
    if (rx_frame & AS5048_ERROR_FLAG) {
        *error_flag = true;
        *raw_angle = rx_frame & AS5048_DATA_MASK; // Містить код помилки
        return true;
    }
    
    *error_flag = false;
    *raw_angle = rx_frame & AS5048_DATA_MASK; // Валідне 14-бітове значення кута
    return true;
}
