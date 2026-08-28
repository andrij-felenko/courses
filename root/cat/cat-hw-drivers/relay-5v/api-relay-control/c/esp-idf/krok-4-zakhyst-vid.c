#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_BTN      GPIO_NUM_26   // кнопка між ніжкою і землею
#define PIN_RELAY    GPIO_NUM_25
#define DEBOUNCE_MS  25            // «тиша» довша за деренчання (кілька мс)

static const bool ACTIVE_LOW = true;
static inline void relay_write(bool on) {
    gpio_set_level(PIN_RELAY, (on ^ ACTIVE_LOW) ? 1 : 0);
}
static int64_t now_ms(void) { return esp_timer_get_time() / 1000; }

void app_main(void) {
    relay_write(false);
    gpio_config_t out = {
        .pin_bit_mask = 1ULL << PIN_RELAY, .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&out));
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_BTN, .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,     // спокій = 1, натиск замикає в 0
        .pull_down_en = GPIO_PULLDOWN_DISABLE, .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&in));

    bool    relay_state  = false;  // логічний стан реле, який перемикаємо
    bool    last_reading = true;   // попереднє СИРЕ читання кнопки
    bool    btn_stable   = true;   // стан, у який кнопка вже устоялась
    int64_t last_edge    = 0;      // коли сире читання востаннє смикнулось

    while (1) {
        bool reading = gpio_get_level(PIN_BTN);

        if (reading != last_reading) {        // смикнулось — перезапуск відліку
            last_edge = now_ms();
            last_reading = reading;
        }

        if (now_ms() - last_edge > DEBOUNCE_MS && reading != btn_stable) {
            btn_stable = reading;
            if (!btn_stable) {                // саме натиск (не відпускання)
                relay_state = !relay_state;
                relay_write(relay_state);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(2));         // опитуємо кнопку раз на 2 мс
    }
}
