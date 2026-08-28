#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

#define KNOCK       GPIO_NUM_4        // вивід S (на ESP32 годиться майже будь-який)
#define LED         GPIO_NUM_2
#define LOCKOUT_US  60000             // глухе вікно після стуку, мкс

static const char *TAG = "knock";
static volatile bool knock_flag = false;   // ставить обробник, скидає цикл

static void IRAM_ATTR on_knock(void *arg) {   // обробник: мусить бути КРИХІТНИЙ
    knock_flag = true;                        // єдина дія — звести прапорець
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << KNOCK,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // спокій = 1, удар тягне до 0
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_NEGEDGE,    // фронт спаду 1→0
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    ESP_ERROR_CHECK(gpio_isr_handler_add(KNOCK, on_knock, NULL));

    int64_t last = 0;                 // час зарахованого стуку, мкс від старту
    unsigned count = 0;
    while (1) {
        int64_t now = esp_timer_get_time();
        if (knock_flag) {                        // обробник щось зафіксував
            knock_flag = false;                  // одразу скидаємо
            if (now - last > LOCKOUT_US) {       // поза вікном — правдивий стук
                last = now;
                count++;
                gpio_set_level(LED, 1);
                ESP_LOGI(TAG, "стук #%u", count);
            }
            // якщо всередині вікна — прапорець з'їдено, це відскок пружини
        }
        if (now - last > 30000) gpio_set_level(LED, 0);   // гасимо світлодіод
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
