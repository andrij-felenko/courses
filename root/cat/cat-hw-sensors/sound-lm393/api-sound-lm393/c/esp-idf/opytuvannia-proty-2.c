#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SOUND GPIO_NUM_4                       // переривання є на будь-якій GPIO
static const char *TAG = "sound";

static volatile bool    hit    = false;        // прапорець «була подія»
static volatile int64_t hit_at = 0;            // коли саме, мкс (для дебаунсу)

// ISR: коротка, без ESP_LOG і vTaskDelay; IRAM_ATTR — обов'язковий
static void IRAM_ATTR on_sound(void *arg) {
    hit    = true;
    hit_at = esp_timer_get_time();
}

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << SOUND,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,     // спадний фронт «1→0»
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));   // спільна служба GPIO-переривань
    ESP_ERROR_CHECK(gpio_isr_handler_add(SOUND, on_sound, NULL));

    while (1) {
        if (hit) {                             // задача лише збирає врожай
            hit = false;
            ESP_LOGI(TAG, "звук (по перериванню)!");
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
