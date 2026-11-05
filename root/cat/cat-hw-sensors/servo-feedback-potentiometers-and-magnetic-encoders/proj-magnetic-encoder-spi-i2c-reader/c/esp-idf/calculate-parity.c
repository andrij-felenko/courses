#include <stdint.h>
#include <stdbool.h>

// Розрахунок парності (even parity) для 15 біт кадру SPI
bool calculate_parity(uint16_t frame) {
    uint16_t v = frame & 0x7FFF;
    v ^= v >> 8;
    v ^= v >> 4;
    v ^= v >> 2;
    v ^= v >> 1;
    return (v & 1) != 0;
}

// Перевірка та розпакування кадру відповіді AS5048
bool as5048_parse_frame(uint16_t raw_frame, uint16_t *angle_out, bool *error_flag) {
    bool expected_parity = calculate_parity(raw_frame);
    bool actual_parity = (raw_frame & 0x8000) != 0;
    
    if (expected_parity != actual_parity) {
        return false; // Помилка паритету, кадр пошкоджено завадою
    }
    
    *error_flag = (raw_frame & 0x4000) != 0;
    *angle_out = raw_frame & 0x3FFF;
    return true;
}
