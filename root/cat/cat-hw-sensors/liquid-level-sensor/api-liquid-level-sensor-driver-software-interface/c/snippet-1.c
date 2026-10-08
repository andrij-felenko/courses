// Заголовочний файл драйвера рівня рідини (C)
#ifndef LIQUID_LEVEL_SENSOR_H
#define LIQUID_LEVEL_SENSOR_H

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t adc_empty;          // Відлік АЦП для порожнього бака (0%)
    uint16_t adc_full;           // Відлік АЦП для повного бака (100%)
    uint16_t max_height_mm;      // Максимальна висота рідини в мм
    uint8_t  median_window;      // Розмір вікна медіанного фільтра (непарне: 3, 5, 7)
    uint8_t  moving_avg_window;  // Розмір вікна рухомого середнього
    float    temp_coef;          // Коефіцієнт температурного дрейфу (%/°C)
    float    temp_calib_celsius; // Температура під час калібрування (°C)
} liquid_level_config_t;

typedef enum {
    LIQUID_LEVEL_OK = 0,
    LIQUID_LEVEL_ERR_INVALID_ARG = -1,
    LIQUID_LEVEL_ERR_LINE_BREAK  = -2,
    LIQUID_LEVEL_ERR_SHORT_CIRCUIT = -3
} liquid_level_status_t;

// Функція ініціалізації драйвера
liquid_level_status_t liquid_level_init(const liquid_level_config_t *config);

#endif // LIQUID_LEVEL_SENSOR_H
