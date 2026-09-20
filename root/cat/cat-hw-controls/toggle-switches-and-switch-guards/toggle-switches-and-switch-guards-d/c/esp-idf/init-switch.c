#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_timer.h"

#define TOGGLE_PIN GPIO_NUM_4
#define DEBOUNCE_TIME_MS 20

typedef struct {
    gpio_num_t pin;
    bool last_raw_state;
    bool stable_state;
    int64_t last_debounce_time;
} debounce_switch_t;

void init_switch(debounce_switch_t *sw, gpio_num_t pin) {
    sw->pin = pin;
    sw->last_raw_state = true;
    sw->stable_state = true;
    sw->last_debounce_time = 0;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << pin),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}

bool update_switch(debounce_switch_t *sw) {
    bool current_raw = gpio_get_level(sw->pin);
    int64_t now_ms = esp_timer_get_time() / 1000;

    if (current_raw != sw->last_raw_state) {
        sw->last_debounce_time = now_ms;
        sw->last_raw_state = current_raw;
    }

    if ((now_ms - sw->last_debounce_time) > DEBOUNCE_TIME_MS) {
        if (current_raw != sw->stable_state) {
            sw->stable_state = current_raw;
            return true; // Стан змінився і стабілізувався
        }
    }
    return false;
}
