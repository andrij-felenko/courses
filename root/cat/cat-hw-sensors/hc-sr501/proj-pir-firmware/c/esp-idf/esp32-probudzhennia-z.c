#include "esp_sleep.h"
#include "esp_log.h"
#include "driver/rtc_io.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_PIR  GPIO_NUM_33      // OUT давача — на RTC-здатну ногу

static const char *TAG = "pir";
RTC_DATA_ATTR static uint32_t boot_count = 0;   // переживає сон у RTC-пам'яті

void app_main(void) {
    boot_count++;

    // Чому прокинулися?
    if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT0) {
        ESP_LOGI(TAG, "Прокинувся від РУХУ. Пробудження #%u", (unsigned)boot_count);
        // --- корисна робота: надіслати сповіщення, зробити кадр тощо ---
        vTaskDelay(pdMS_TO_TICKS(500));
    } else {
        // Перший старт (не від руху): дати давачу прогрітися перед сном.
        ESP_LOGI(TAG, "Холодний старт — прогрів давача 60 с");
        vTaskDelay(pdMS_TO_TICKS(60000));   // чекати можна: нам однаково нічого робити
    }

    // Налаштувати пробудження по фронту OUT і заснути.
    ESP_ERROR_CHECK(rtc_gpio_pulldown_en(PIN_PIR));   // тримати ногу в "0" під час сну
    ESP_ERROR_CHECK(rtc_gpio_pullup_dis(PIN_PIR));
    ESP_ERROR_CHECK(esp_sleep_enable_ext0_wakeup(PIN_PIR, 1));  // 1 = будити по HIGH

    ESP_LOGI(TAG, "Засинаю. Розбудить рух.");
    esp_deep_sleep_start();   // нижче не виконається: після пробудження app_main почнеться заново
}
