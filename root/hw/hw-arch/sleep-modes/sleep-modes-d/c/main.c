#include "esp_sleep.h"
#include "esp_log.h"

#define WAKE_BUTTON_GPIO   GPIO_NUM_33   // RTC-ніжка: годиться для deep-sleep
#define SLEEP_PERIOD_US    (10ULL * 60 * 1000000ULL)  // 10 хв у мкс

static const char *TAG = "sleep";

// Лічильник переживає deep-sleep лише в RTC-пам'яті — звичайна змінна
// після перезапуску обнулиться, бо SRAM знеструмлено.
RTC_DATA_ATTR int boot_count = 0;

void handle_wakeup(void) {
    esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
    switch (cause) {
        case ESP_SLEEP_WAKEUP_TIMER:
            ESP_LOGI(TAG, "Розбудив таймер: плановий замір");
            // тут: зняти давач, відіслати число
            break;
        case ESP_SLEEP_WAKEUP_EXT0:
            ESP_LOGI(TAG, "Розбудила кнопка: поряд людина");
            // тут: увімкнути екран, лишитися активним довше
            break;
        default:
            ESP_LOGI(TAG, "Холодний старт (не з deep-sleep)");
            break;
    }
}

void app_main(void) {
    // deep-sleep щоразу заходить сюди заново, з чистою SRAM
    boot_count++;
    ESP_LOGI(TAG, "Пробудження №%d", boot_count);

    handle_wakeup();          // зреагувати на причину
    // ... корисна робота (замір, передача) ...

    // Налаштувати ОБИДВА джерела перед сном: спрацює перше з них
    esp_sleep_enable_timer_wakeup(SLEEP_PERIOD_US);
    esp_sleep_enable_ext0_wakeup(WAKE_BUTTON_GPIO, 0);  // 0 = будити низьким рівнем

    ESP_LOGI(TAG, "Засинаю в deep-sleep...");
    esp_deep_sleep_start();
    // Рядків після цього немає сенсу писати: чіп прокинеться з app_main(),
    // а не звідси.
}
