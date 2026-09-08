/* ============================================================================
   krok-3-load-switch-sequencing.c — ESP-IDF: послідовний старт шин
   ========================================================================== */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "POWER_SEQ";

#define GPIO_PERIPH_SENSORS  GPIO_NUM_19
#define GPIO_PERIPH_RADIO    GPIO_NUM_21

void power_sequencing_boot(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_PERIPH_SENSORS) | (1ULL << GPIO_PERIPH_RADIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    // Обидва вимкнені (Active LOW)
    gpio_set_level(GPIO_PERIPH_SENSORS, 1);
    gpio_set_level(GPIO_PERIPH_RADIO, 1);

    ESP_LOGI(TAG, "Етап 1: Очікування заряду конденсаторів MB102...");
    vTaskDelay(pdMS_TO_TICKS(150));

    ESP_LOGI(TAG, "Етап 2: Увімкнення сенсорів...");
    gpio_set_level(GPIO_PERIPH_SENSORS, 0);
    vTaskDelay(pdMS_TO_TICKS(80));

    ESP_LOGI(TAG, "Етап 3: Увімкнення радіомодуля (Wi-Fi/ESP-NOW)...");
    gpio_set_level(GPIO_PERIPH_RADIO, 0);
    vTaskDelay(pdMS_TO_TICKS(50));

    ESP_LOGI(TAG, "Система готова: старт мережевого стека.");
}
