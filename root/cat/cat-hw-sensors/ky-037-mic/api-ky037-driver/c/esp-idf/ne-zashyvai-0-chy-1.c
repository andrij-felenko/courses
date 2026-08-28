#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#define SOUND_GPIO  GPIO_NUM_4          // DO давача — на будь-який вхідний GPIO
static const char *TAG = "ky037";

static int idle_level;                  // рівень, який плата тримає в ТИШІ

static void sound_begin(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << SOUND_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,   // підтяжка вже стоїть на модулі
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    vTaskDelay(pdMS_TO_TICKS(50));             // дати входу усталитися
    idle_level = gpio_get_level(SOUND_GPIO);   // у тиші — «спокій» цієї плати
    ESP_LOGI(TAG, "рівень спокою DO = %d (подія — відхилення від нього)", idle_level);
}

// true — коли DO відійшов від спокою, тобто звук ПЕРЕВИЩИВ поріг.
static inline bool is_loud(void) {
    return gpio_get_level(SOUND_GPIO) != idle_level;
}

void app_main(void) {
    sound_begin();
    while (1) {
        ESP_LOGI(TAG, "%s", is_loud() ? "гучно" : "тихо");
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
