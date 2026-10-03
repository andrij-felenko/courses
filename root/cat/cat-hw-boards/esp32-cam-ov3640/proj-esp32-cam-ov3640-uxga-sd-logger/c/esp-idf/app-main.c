#include "esp_log.h"
#include "driver/gpio.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_sleep.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PWR_CTRL_GPIO GPIO_NUM_13
static const char *TAG = "PWR_MGR";

void app_main(void) {
    // Налаштування виводу керування P-MOSFET ключем
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PWR_CTRL_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    
    // Активація живлення (низький рівень відкриває P-MOSFET)
    gpio_set_level(PWR_CTRL_GPIO, 0);
    ESP_LOGI(TAG, "Подача живлення на периферійні вузли...");

    // Апаратна затримка для стабілізації LDO та конденсаторів
    vTaskDelay(pdMS_TO_TICKS(50));

    // Перевірка причини пробудження ESP32
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    ESP_LOGI(TAG, "Причина пробудження: %d", wakeup_reason);

    // Зйомка UXGA кадру та збереження на SDMMC
    // ...

    // Знеструмлення периферії перед зануренням у сон
    gpio_set_level(PWR_CTRL_GPIO, 1);
    ESP_LOGI(TAG, "Периферію вимкнено. Перехід у Deep Sleep.");

    // Налаштування таймера сну на 60 секунд
    esp_sleep_enable_timer_wakeup(60 * 1000000ULL);
    esp_deep_sleep_start();
}
