#include <stdint.h>
#include <stdbool.h>

// Статуси повернення драйвера TCRT5000
typedef enum {
    TCRT5000_OK = 0,
    TCRT5000_ERR_INVALID_ARG,
    TCRT5000_ERR_ADC_FAIL,
    TCRT5000_ERR_SATURATION,
    TCRT5000_ERR_DISCONNECTED
} tcrt5000_err_t;

// Конфігураційна структура драйвера TCRT5000
typedef struct {
    int adc_channel;        // Номер каналу ADC (AO)
    int gpio_digital;       // Номер виводу GPIO (DO), -1 якщо не використовується
    int gpio_emitter_ctrl;  // Номер виводу керування ІЧ-діодом, -1 якщо увімкнено постійно
    uint16_t threshold_low;  // Нижня межа гістерезису
    uint16_t threshold_high; // Верхня межа гістерезису
} tcrt5000_config_t;

// Контекстний об'єкт драйвера TCRT5000
typedef struct {
    tcrt5000_config_t config;
    uint16_t last_raw_value;
    uint16_t filtered_value;
    bool is_calibrated;
    bool initialized;
} tcrt5000_t;

// Ініціалізація драйвера TCRT5000 у стилі C
tcrt5000_err_t tcrt5000_init(tcrt5000_t *dev, const tcrt5000_config_t *cfg) {
    if (!dev || !cfg) {
        return TCRT5000_ERR_INVALID_ARG;
    }
    
    dev->config = *cfg;
    dev->last_raw_value = 0;
    dev->filtered_value = 0;
    dev->is_calibrated = false;
    
    // Ініціалізація апаратних периферійних модулів платформи
    dev->initialized = true;
    return TCRT5000_OK;
}
