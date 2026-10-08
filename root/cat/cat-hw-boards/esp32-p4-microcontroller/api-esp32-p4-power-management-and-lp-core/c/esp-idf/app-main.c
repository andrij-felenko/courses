#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_sleep.h"
#include "esp_log.h"
#include "driver/gpio.h"

static const char *TAG = "PMU_POWER_MGMT";

#define WAKEUP_GPIO_NUM     GPIO_NUM_9
#define SLEEP_TIMER_US      (5 * 1000 * 1000) // 5 секунд у мікросекундах

void app_main(void)
{
    // Отримання причини останнього пробудження системи
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();

    switch (wakeup_reason) {
        case ESP_SLEEP_WAKEUP_TIMER:
            ESP_LOGI(TAG, "Пробудження викликано таймером PMU");
            break;
        case ESP_SLEEP_WAKEUP_GPIO:
        case ESP_SLEEP_WAKEUP_EXT1:
            ESP_LOGI(TAG, "Пробудження викликано зовнішнім сигналом GPIO");
            break;
        default:
            ESP_LOGI(TAG, "Первинний запуск або холодний скид системи");
            break;
    }

    // Налаштування GPIO9 як джерела пробудження за низьким рівнем
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << WAKEUP_GPIO_NUM),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);

    // Реєстрація джерел пробудження у драйвері PMU
    ESP_ERROR_CHECK(esp_sleep_enable_timer_wakeup(SLEEP_TIMER_US));
    ESP_ERROR_CHECK(esp_sleep_enable_ext1_wakeup(1ULL << WAKEUP_GPIO_NUM, ESP_EXT1_WAKEUP_ANY_LOW));

    ESP_LOGI(TAG, "Вхід у режим Light-sleep на 5 секунд...");
    vTaskDelay(pdMS_TO_TICKS(100)); // Завершення виводу логів
    
    // Перехід у режим легкого сну (HP SRAM зберігає стан)
    esp_light_sleep_start();

    ESP_LOGI(TAG, "Пробудження з Light-sleep виконано. Підготовка до Deep-sleep...");
    vTaskDelay(pdMS_TO_TICKS(1000));

    // Перехід у режим глибокого сну (HP-домен знеструмлюється)
    ESP_LOGI(TAG, "Перехід у Deep-sleep. HP-домен буде вимкнено.");
    esp_deep_sleep_start();
}
