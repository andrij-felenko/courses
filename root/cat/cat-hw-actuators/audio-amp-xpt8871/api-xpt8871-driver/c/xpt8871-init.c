// Модульний C-драйвер підсилювача XPT8871 для середовища ESP-IDF
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_err.h"

typedef enum {
    XPT_STATE_SHUTDOWN = 0,
    XPT_STATE_POWERING_UP,
    XPT_STATE_ACTIVE
} xpt_state_t;

typedef struct {
    gpio_num_t pin_shdn;
    uint32_t   twu_ms;
    int64_t    start_time_us;
    xpt_state_t state;
} xpt8871_dev_t;

esp_err_t xpt8871_init(xpt8871_dev_t *dev, gpio_num_t pin, uint32_t twu_ms) {
    if (!dev) return ESP_ERR_INVALID_ARG;

    dev->pin_shdn = pin;
    dev->twu_ms = twu_ms;
    dev->state = XPT_STATE_SHUTDOWN;
    dev->start_time_us = 0;

    gpio_set_level(pin, 0);

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    return gpio_config(&io_conf);
}

void xpt8871_enable(xpt8871_dev_t *dev) {
    if (dev->state == XPT_STATE_SHUTDOWN) {
        gpio_set_level(dev->pin_shdn, 1);
        dev->start_time_us = esp_timer_get_time();
        dev->state = XPT_STATE_POWERING_UP;
    }
}

void xpt8871_disable(xpt8871_dev_t *dev) {
    gpio_set_level(dev->pin_shdn, 0);
    dev->state = XPT_STATE_SHUTDOWN;
}

bool xpt8871_is_ready(xpt8871_dev_t *dev) {
    if (dev->state == XPT_STATE_POWERING_UP) {
        int64_t elapsed_ms = (esp_timer_get_time() - dev->start_time_us) / 1000;
        if (elapsed_ms >= dev->twu_ms) {
            dev->state = XPT_STATE_ACTIVE;
        }
    }
    return (dev->state == XPT_STATE_ACTIVE);
}
