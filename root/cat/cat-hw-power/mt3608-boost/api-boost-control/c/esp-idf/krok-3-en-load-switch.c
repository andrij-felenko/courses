/* ============================================================================
   krok-3-en-load-switch.c — ESP-IDF: керування піном EN та ключем навантаження
   ========================================================================== */

#include <stdio.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "MT3608_CTRL";

#define GPIO_MT3608_EN       GPIO_NUM_25  // Пін 4 мікросхеми MT3608 (HIGH = ON)
#define GPIO_LOAD_GATE       GPIO_NUM_26  // Силовий P-MOSFET ключ (LOW = ON)

void mt3608_control_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_MT3608_EN) | (1ULL << GPIO_LOAD_GATE),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    // Старт у вимкненому стані
    gpio_set_level(GPIO_MT3608_EN, 0);   // Зупинка генерації ШІМ
    gpio_set_level(GPIO_LOAD_GATE, 1);  // Розрив лінії навантаження (повні 0 В)
}

void mt3608_enable_power(bool enable) {
    if (enable) {
        ESP_LOGI(TAG, "Крок 1: Запуск генератора MT3608...");
        gpio_set_level(GPIO_MT3608_EN, 1);
        vTaskDelay(pdMS_TO_TICKS(15)); // Чекаємо наростання напруги на Cout

        ESP_LOGI(TAG, "Крок 2: Підключення високовольтного навантаження...");
        gpio_set_level(GPIO_LOAD_GATE, 0);
    } else {
        ESP_LOGI(TAG, "Відключення навантаження та переведення в сон...");
        gpio_set_level(GPIO_LOAD_GATE, 1);
        gpio_set_level(GPIO_MT3608_EN, 0);
    }
}
