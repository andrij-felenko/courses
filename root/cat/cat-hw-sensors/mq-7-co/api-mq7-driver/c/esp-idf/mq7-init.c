#include "esp_err.h"
#include "driver/ledc.h"
#include "esp_adc/adc_oneshot.h"

typedef enum {
    MQ7_STATE_UNINIT = 0,
    MQ7_STATE_HIGH_HEAT,
    MQ7_STATE_LOW_HEAT,
    MQ7_STATE_FAULT
} mq7_state_t;

typedef enum {
    MQ7_OK = 0,
    MQ7_ERR_INVALID_ARG,
    MQ7_ERR_HEATER_FAULT,
    MQ7_ERR_TIMEOUT
} mq7_error_t;

esp_err_t mq7_init(mq7_t *dev, const mq7_config_t *cfg) {
    if (dev == NULL || cfg == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    
    dev->config = *cfg;
    dev->state = MQ7_STATE_HIGH_HEAT;
    dev->last_state_change_ms = 0;
    dev->last_tick_ms = 0;
    dev->raw_adc_value = 0;
    dev->rs_kohm = 0.0f;
    dev->co_ppm = 0.0f;
    dev->data_ready = false;
    dev->error_code = MQ7_OK;

    // Конфігурація ШІМ для керування ключем живлення нагрівача (100% на старті)
    ledc_channel_config_t ledc_channel = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .timer_sel  = LEDC_TIMER_0,
        .intr_type  = LEDC_INTR_DISABLE,
        .gpio_num   = cfg->pwm_gpio_pin,
        .duty       = 255, // 100% заповнення для 8-бітного таймера (5.0 В)
        .hpoint     = 0
    };
    ledc_channel_config(&ledc_channel);

    return ESP_OK;
}
