#include <stdint.h>
#include <stdbool.h>
#include "driver/mcpwm_cap.h"

// Перерахунок тривалості імпульсу у мікросекундах у 14-бітний кут AS5048
bool decode_as5048_pwm(uint32_t high_pulse_us, uint32_t period_us, float *angle_deg) {
    // Перевірка допустимості періоду ШІМ (1025 мкс +- 5%)
    if (period_us < 970 || period_us > 1080) {
        return false; // Помилка частоти сигналу або втрата зв'язку
    }

    float t_high = (float)high_pulse_us;
    float t_init = 4.0f;    // Стартовий інтервал 4 мкс (16 бітів)
    float t_max  = 1023.0f; // Максимальний робочий інтервал тривалості

    if (t_high < t_init) t_high = t_init;
    float t_data = t_high - t_init;
    if (t_data > t_max) t_data = t_max;

    float raw_angle = (t_data / t_max) * 16383.0f;
    *angle_deg = (raw_angle * 360.0f) / 16384.0f;
    return true;
}
