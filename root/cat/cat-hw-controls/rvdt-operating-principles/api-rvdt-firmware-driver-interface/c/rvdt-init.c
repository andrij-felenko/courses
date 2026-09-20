#include <stdint.h>
#include <stdbool.h>

// Статуси повернення функцій драйвера RVDT
typedef enum {
    RVDT_STATUS_OK               = 0,
    RVDT_STATUS_ERR_PARAM        = 1,
    RVDT_STATUS_ERR_EXCITATION   = 2,
    RVDT_STATUS_ERR_OPEN_WINDING = 3,
    RVDT_STATUS_ERR_OUT_OF_RANGE = 4
} rvdt_status_t;

// Структура конфігурації апаратного драйвера RVDT
typedef struct {
    uint32_t excitation_freq_hz;     // Частота первинного збудження (Герц)
    float    excitation_amplitude_v; // Амплітуда збудження (Вольт)
    float    sensitivity_v_v_deg;    // Чутливість давача (В/В/град)
    uint16_t adc_max_raw;            // Максимальний відлік АЦП (наприклад, 4095)
} rvdt_config_t;

// Контекст виконання драйвера RVDT
typedef struct {
    rvdt_config_t config;
    float zero_offset_deg;           // Калібрувальний зсув нуля (градуси)
    float scale_factor;              // Масштабний коефіцієнт
    bool  is_initialized;
} rvdt_handle_t;

// Ініціалізація драйвера RVDT
rvdt_status_t rvdt_init(rvdt_handle_t *handle, const rvdt_config_t *config) {
    if (!handle || !config) {
        return RVDT_STATUS_ERR_PARAM;
    }
    if (config->excitation_freq_hz < 400 || config->excitation_freq_hz > 20000) {
        return RVDT_STATUS_ERR_EXCITATION;
    }
    handle->config = *config;
    handle->zero_offset_deg = 0.0f;
    handle->scale_factor = 1.0f;
    handle->is_initialized = true;
    return RVDT_STATUS_OK;
}
