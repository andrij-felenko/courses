#include <stdint.h>

// Обчислення коефіцієнта заповнення ШІМ (0-255) за аналоговим значенням аудіосигналу
uint8_t calculate_pwm_duty(int16_t audio_sample) {
    // Вхідний сигнал audio_sample у діапазоні від -32768 до +32767
    // Нормалізація в діапазон від 0 до 255 для 8-бітного таймера ШІМ
    int32_t normalized = ((int32_t)audio_sample + 32768) >> 8;
    
    if (normalized < 0) {
        normalized = 0;
    } else if (normalized > 255) {
        normalized = 255;
    }
    
    return (uint8_t)normalized;
}
