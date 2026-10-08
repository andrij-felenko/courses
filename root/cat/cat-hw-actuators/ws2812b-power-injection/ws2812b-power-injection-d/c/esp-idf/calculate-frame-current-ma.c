#include <stdio.h>
#include <stdint.h>
#include "esp_attr.h"
#include "esp_log.h"

#define NUM_PIXELS 300
#define CURRENT_PER_SUBPIXEL_UA 20000 // 20 мА на кожен RGB підпіксель
#define QUIESCENT_CURRENT_PER_PIXEL_UA 1000 // 1 мА струм спокою внутрішнього драйвера
#define MAX_ALLOWED_CURRENT_MA 8000 // Ліміт 8 Ампер

typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} pixel_rgb_t;

pixel_rgb_t frame_buffer[NUM_PIXELS];

// Обчислення оціночного струму споживання кадру в міліамперах
uint32_t calculate_frame_current_ma(const pixel_rgb_t* buffer, uint16_t length) {
    uint64_t total_microamps = 0;
    for (uint16_t i = 0; i < length; i++) {
        total_microamps += QUIESCENT_CURRENT_PER_PIXEL_UA;
        total_microamps += ((uint32_t)buffer[i].r * CURRENT_PER_SUBPIXEL_UA) / 255;
        total_microamps += ((uint32_t)buffer[i].g * CURRENT_PER_SUBPIXEL_UA) / 255;
        total_microamps += ((uint32_t)buffer[i].b * CURRENT_PER_SUBPIXEL_UA) / 255;
    }
    return (uint32_t)(total_microamps / 1000);
}

// Програмне масштабування яскравості для дотримання струмового ліміту
void apply_power_limit(pixel_rgb_t* buffer, uint16_t length, uint32_t max_current_ma) {
    uint32_t estimated_ma = calculate_frame_current_ma(buffer, length);
    if (estimated_ma > max_current_ma) {
        float scale = (float)max_current_ma / (float)estimated_ma;
        for (uint16_t i = 0; i < length; i++) {
            buffer[i].r = (uint8_t)(buffer[i].r * scale);
            buffer[i].g = (uint8_t)(buffer[i].g * scale);
            buffer[i].b = (uint8_t)(buffer[i].b * scale);
        }
    }
}
