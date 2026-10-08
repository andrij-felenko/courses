#include <stdint.h>
#include <stdbool.h>

// Структура конфігурації драйвера LM35
typedef struct {
    float vref_mv;          // Опорна напруга АЦП у мілівольтах (наприклад, 1100.0f)
    uint8_t adc_bits;       // Розрядність АЦП у бітах (наприклад, 10 або 12)
    float scale_factor;     // Коефіцієнт масштабування (номінально 1.0f)
    float offset_celsius;   // Коефіцієнт зміщення нуля в градусах Цельсія (номінально 0.0f)
} lm35_config_t;

// Структура стану екземпляра драйвера
typedef struct {
    lm35_config_t config;
    float lsb_mv;           // Обчислена величина LSB у мілівольтах
    uint32_t max_adc_raw;   // Максимальне значення сирого коду (2^N - 1)
} lm35_t;

// Функція ініціалізації драйвера
bool lm35_init(lm35_t *dev, const lm35_config_t *config) {
    if (dev == NULL || config == NULL) {
        return false;
    }
    if (config->adc_bits == 0 || config->adc_bits > 16 || config->vref_mv <= 0.0f) {
        return false;
    }

    dev->config = *config;
    dev->max_adc_raw = (1U << config->adc_bits) - 1U;
    dev->lsb_mv = config->vref_mv / (float)dev->max_adc_raw;

    return true;
}
