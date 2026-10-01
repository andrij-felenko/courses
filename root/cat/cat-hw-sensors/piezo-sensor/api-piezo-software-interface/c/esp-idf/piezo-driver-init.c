#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t adc_channel;       // Номер каналу АЦП
    uint32_t sample_rate_hz;   // Частота дискретизації в Гц
    uint8_t resolution_bits;   // Розрядність АЦП
} piezo_config_t;

typedef struct {
    piezo_config_t config;
    uint16_t baseline;
    bool is_initialized;
} piezo_driver_t;

bool piezo_driver_init(piezo_driver_t *driver, const piezo_config_t *config) {
    if (!driver || !config || config->sample_rate_hz == 0) {
        return false;
    }
    driver->config = *config;
    driver->baseline = 0;
    driver->is_initialized = true;
    return true;
}
