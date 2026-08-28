#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_PIR    GPIO_NUM_33     // OUT давача
#define PIN_RELAY  GPIO_NUM_25     // вхід релейного модуля (активний "1")

#define WARMUP_MS    60000U        // прогрів: перша хвилина — не вірити
#define DEBOUNCE_MS  40U           // скільки тримати рівень, щоб повірити
#define HOLD_MS      5000U         // власний "хвіст" після зникнення руху

static const char *TAG = "pir";
static inline uint32_t now_ms(void) { return (uint32_t)(esp_timer_get_time() / 1000); }

void app_main(void) {
    gpio_config_t in = {                       // OUT сам штовхає рівень — підтяжка не потрібна
        .pin_bit_mask = 1ULL << PIN_PIR,   .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&in));
    gpio_config_t out = {
        .pin_bit_mask = 1ULL << PIN_RELAY, .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&out));
    gpio_set_level(PIN_RELAY, 0);              // почати з вимкненого світла

    uint32_t t_boot = now_ms(), t_edge = t_boot, t_last_motion = 0;
    int raw_prev = gpio_get_level(PIN_PIR), stable = 0;
    bool light_on = false;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(10));         // крок циклу; заразом віддаємо час іншим задачам
        uint32_t now = now_ms();

        // --- Шар 1: гасіння прогріву. Першу хвилину виходу не віримо. ---
        if (now - t_boot < WARMUP_MS) { gpio_set_level(PIN_RELAY, 0); continue; }

        // --- Шар 2: дебаунс. Рівень мусить протриматися DEBOUNCE_MS. ---
        int raw = gpio_get_level(PIN_PIR);
        if (raw != raw_prev) { t_edge = now; raw_prev = raw; }
        if (now - t_edge >= DEBOUNCE_MS) stable = raw;
        if (stable) t_last_motion = now;

        // --- Шар 3: рішення про світло з власним "хвостом" HOLD_MS. ---
        bool want_on = (now - t_last_motion < HOLD_MS);
        if (want_on != light_on) {
            light_on = want_on;
            gpio_set_level(PIN_RELAY, light_on ? 1 : 0);
            ESP_LOGI(TAG, "%s", light_on ? "світло УВІМК" : "світло вимк");
        }
    }
}
