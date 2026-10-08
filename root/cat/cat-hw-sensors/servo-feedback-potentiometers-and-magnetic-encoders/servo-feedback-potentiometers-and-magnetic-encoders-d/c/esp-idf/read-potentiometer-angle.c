// Зчитування потенціометра та аналогова фільтрація кута у C (ESP-IDF)
#include <stdio.h>
#include <stdint.h>
#include "esp_adc/adc_oneshot.h"

#define ADC_MAX_VAL      4095.0f // 12-бітний АЦП
#define SERVO_MAX_ANGLE  180.0f  // Максимальний робочий кут (градуси)
#define ALPHA            0.15f   // Коефіцієнт експоненціального фільтра

// Структура стану потенціометричного давача
typedef struct {
    adc_oneshot_unit_handle_t adc_handle;
    adc_channel_t channel;
    float filtered_angle;
    uint16_t adc_min; // Межа мертвої зони (0°)
    uint16_t adc_max; // Межа мертвої зони (180°)
} ServoPotentiometer_t;

// Обчислення кута з врахуванням мертвих зон та фільтрації
float read_potentiometer_angle(ServoPotentiometer_t *sensor) {
    int raw_adc = 0;
    adc_oneshot_read(sensor->adc_handle, sensor->channel, &raw_adc);

    // Обрізання мертвих зон на краях доріжки
    if (raw_adc < sensor->adc_min) raw_adc = sensor->adc_min;
    if (raw_adc > sensor->adc_max) raw_adc = sensor->adc_max;

    // Масштабування напруги АЦП у кутове положення
    float norm = (float)(raw_adc - sensor->adc_min) / (float)(sensor->adc_max - sensor->adc_min);
    float current_angle = norm * SERVO_MAX_ANGLE;

    // Експоненціальне згладжування шуму струмознімача
    sensor->filtered_angle = (ALPHA * current_angle) + ((1.0f - ALPHA) * sensor->filtered_angle);
    return sensor->filtered_angle;
}
