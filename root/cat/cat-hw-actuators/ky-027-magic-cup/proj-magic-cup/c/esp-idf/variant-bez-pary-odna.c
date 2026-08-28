// ── Одна KY-027 як плавний індикатор нахилу (ESP-IDF, ШІМ через LEDC) ──
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_S   GPIO_NUM_4     // вихід вимикача (цифровий вхід)
#define PIN_L   GPIO_NUM_18    // світлодіод — канал LEDC 0
#define TILTED  0              // рівень S, що означає «нахилено»

typedef struct { gpio_num_t pin; bool stable; bool last_raw; int64_t changed_us; } debounced_t;
#define DEBOUNCE_US 25000

static void debounce_begin(debounced_t *d, gpio_num_t pin) {
    gpio_config_t cfg = { .pin_bit_mask = 1ULL << pin, .mode = GPIO_MODE_INPUT,
                          .pull_up_en = GPIO_PULLUP_DISABLE,
                          .pull_down_en = GPIO_PULLDOWN_DISABLE,
                          .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    d->pin = pin; d->stable = gpio_get_level(pin);
    d->last_raw = d->stable; d->changed_us = esp_timer_get_time();
}
static bool debounce_read(debounced_t *d) {
    bool raw = gpio_get_level(d->pin);
    if (raw != d->last_raw) { d->last_raw = raw; d->changed_us = esp_timer_get_time(); }
    if (raw != d->stable && esp_timer_get_time() - d->changed_us >= DEBOUNCE_US) d->stable = raw;
    return d->stable;
}

#define STEP 4

void app_main(void) {
    static debounced_t sw;
    debounce_begin(&sw, PIN_S);

    ledc_timer_config_t t = { .speed_mode = LEDC_LOW_SPEED_MODE, .timer_num = LEDC_TIMER_0,
                              .duty_resolution = LEDC_TIMER_8_BIT,   // 0..255
                              .freq_hz = 5000, .clk_cfg = LEDC_AUTO_CLK };
    ESP_ERROR_CHECK(ledc_timer_config(&t));
    ledc_channel_config_t c = { .gpio_num = PIN_L, .speed_mode = LEDC_LOW_SPEED_MODE,
                                .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0,
                                .intr_type = LEDC_INTR_DISABLE, .duty = 0, .hpoint = 0 };
    ESP_ERROR_CHECK(ledc_channel_config(&c));

    uint8_t bright = 0;                  // поточна яскравість 0..255
    while (1) {
        bool tilted = (debounce_read(&sw) == TILTED);
        // Нахилено → повземо до 255; рівно → сповзаємо до 0. Обидва — з упором.
        int next = (int)bright + (tilted ? +STEP : -STEP);
        if (next < 0) next = 0;
        if (next > 255) next = 255;
        bright = (uint8_t)next;

        ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, bright));
        ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0));
        vTaskDelay(pdMS_TO_TICKS(6));    // темп наростання/згасання
    }
}
