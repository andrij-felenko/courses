#include <stdint.h>
#include <math.h>

// Розрахунок байта регістру GAIN (0x00) для OV2640
uint8_t ov2640_calculate_gain_reg(float target_gain) {
    if (target_gain <= 1.0f) return 0x00;
    if (target_gain >= 32.0f) return 0xFF;

    uint8_t reg_val = 0;
    float current_gain = target_gain;

    // Перевірка старших ступенів підсилення B7 (2.0x)
    if (current_gain >= 2.0f) {
        reg_val |= (1 << 7);
        current_gain /= 2.0f;
    }
    // B6 (1.5x)
    if (current_gain >= 1.5f) {
        reg_val |= (1 << 6);
        current_gain /= 1.5f;
    }
    // B5 (1.25x)
    if (current_gain >= 1.25f) {
        reg_val |= (1 << 5);
        current_gain /= 1.25f;
    }
    // B4 (1.125x)
    if (current_gain >= 1.125f) {
        reg_val |= (1 << 4);
        current_gain /= 1.125f;
    }

    // Обчислення точного 4-бітного лінійного кроку
    int step = (int)roundf((current_gain - 1.0f) * 16.0f);
    if (step < 0) step = 0;
    if (step > 15) step = 15;

    reg_val |= (uint8_t)step;
    return reg_val;
}
