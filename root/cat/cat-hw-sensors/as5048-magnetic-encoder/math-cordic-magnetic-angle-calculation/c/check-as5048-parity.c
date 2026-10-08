#include <stdint.h>
#include <stdbool.h>

// Перевірка біта парної парності 16-бітного кадру SPI
bool check_as5048_parity(uint16_t frame) {
    uint16_t temp = frame;
    temp ^= temp >> 8;
    temp ^= temp >> 4;
    temp ^= temp >> 2;
    temp ^= temp >> 1;
    return (temp & 1) == 0; // Повертає true, якщо кількість одиниць парна
}

// Перетворення 14-бітного коду CORDIC у кут в градусах
float convert_code_to_degrees(uint16_t raw_frame) {
    uint16_t angle_code = raw_frame & 0x3FFF; // Виділення 14 біт кута
    return (float)angle_code * (360.0f / 16384.0f);
}
