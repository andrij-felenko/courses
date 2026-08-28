#include <stdbool.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_RELAY  GPIO_NUM_25

// Уся полярність модуля живе ТУТ, в одному місці.
static const bool ACTIVE_LOW = true;

static inline void relay_write(bool on) {
    // XOR з ACTIVE_LOW інвертує рівень лише коли модуль active-low.
    gpio_set_level(PIN_RELAY, (on ^ ACTIVE_LOW) ? 1 : 0);
}

static inline void relay_on(void)  { relay_write(true);  }
static inline void relay_off(void) { relay_write(false); }

void app_main(void) {
    relay_off();                     // безпечний рівень СПЕРШУ (див. крок 1)
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_RELAY, .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));

    while (1) {
        relay_on();
        vTaskDelay(pdMS_TO_TICKS(1000));
        relay_off();
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
