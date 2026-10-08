#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_timer.h"

typedef enum {
    WATER_FLOW_OK = 0,
    WATER_FLOW_ERR_INVALID_ARG = -1,
    WATER_FLOW_ERR_NOT_INITIALIZED = -2,
    WATER_FLOW_ERR_OUT_OF_RANGE = -3,
    WATER_FLOW_ERR_TURBINE_JAMMED = -4
} water_flow_err_t;

typedef struct {
    gpio_num_t gpio_num;
    float k_factor;             // Коефіцієнт K (Гц / (л/хв)), наприклад 7.5
    uint32_t sample_period_ms;  // Період таймера у мс, наприклад 1000
} water_flow_config_t;

typedef struct {
    gpio_num_t gpio_num;
    float k_factor;
    uint32_t sample_period_ms;
    volatile uint32_t pulse_count_isr; // Лічильник імпульсів для ISR
    float current_flow_lmin;
    double total_volume_liters;
    esp_timer_handle_t timer_handle;
    bool is_initialized;
} water_flow_handle_t;

static void IRAM_ATTR water_flow_gpio_isr_handler(void *arg) {
    water_flow_handle_t *dev = (water_flow_handle_t *)arg;
    dev->pulse_count_isr++;
}

static void water_flow_timer_callback(void *arg) {
    water_flow_handle_t *dev = (water_flow_handle_t *)arg;
    
    // Атомарне читання та скидання лічильника імпульсів
    uint32_t pulses = dev->pulse_count_isr;
    dev->pulse_count_isr = 0;
    
    float dt_sec = (float)dev->sample_period_ms / 1000.0f;
    float freq_hz = (float)pulses / dt_sec;
    
    // Розрахунок миттєвої витрати (л/хв)
    dev->current_flow_lmin = freq_hz / dev->k_factor;
    
    // Інтегрування накопиченого об'єму (літри)
    float added_liters = dev->current_flow_lmin * (dt_sec / 60.0f);
    dev->total_volume_liters += added_liters;
}

water_flow_err_t water_flow_init(water_flow_handle_t *dev, const water_flow_config_t *cfg) {
    if (!dev || !cfg || cfg->k_factor <= 0.0f || cfg->sample_period_ms == 0) {
        return WATER_FLOW_ERR_INVALID_ARG;
    }

    dev->gpio_num = cfg->gpio_num;
    dev->k_factor = cfg->k_factor;
    dev->sample_period_ms = cfg->sample_period_ms;
    dev->pulse_count_isr = 0;
    dev->current_flow_lmin = 0.0f;
    dev->total_volume_liters = 0.0;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << cfg->gpio_num),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_POSEDGE
    };
    gpio_config(&io_conf);

    gpio_isr_handler_add(cfg->gpio_num, water_flow_gpio_isr_handler, (void *)dev);

    esp_timer_create_args_t timer_args = {
        .callback = &water_flow_timer_callback,
        .arg = (void *)dev,
        .name = "water_flow_timer"
    };
    esp_timer_create(&timer_args, &dev->timer_handle);
    esp_timer_start_periodic(dev->timer_handle, cfg->sample_period_ms * 1000ULL);

    dev->is_initialized = true;
    return WATER_FLOW_OK;
}
