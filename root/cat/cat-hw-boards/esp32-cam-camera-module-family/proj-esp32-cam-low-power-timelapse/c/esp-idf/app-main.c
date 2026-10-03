#include "esp_sleep.h"
#include "driver/gpio.h"
#include "driver/rtc_io.h"
#include "esp_log.h"

#define PIR_GPIO_NUM GPIO_NUM_13
#define TIME_TO_SLEEP_SEC 3600ULL

static const char *TAG = "POWER_MGMT";

void app_main(void) {
    // Визначення джерела пробудження системи
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();

    switch (wakeup_reason) {
        case ESP_SLEEP_WAKEUP_TIMER:
            ESP_LOGI(TAG, "Пробудження за RTC-таймером: виконання таймлапс-знімка");
            break;
        case ESP_SLEEP_WAKEUP_EXT0:
            ESP_LOGI(TAG, "Пробудження від PIR-датчика: виявлено рух в зоні спостереження");
            break;
        default:
            ESP_LOGI(TAG, "Первинне включення або скидання системи");
            break;
    }

    // Подаємо живлення на камеру через MOSFET-ключ та ініціалізуємо сенсор OV2640
    // (тут виконується подача кадру та збереження його на microSD)

    // Конфігуруємо RTC-таймер на 1 годину (переведення секунд у мікросекунди)
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_SEC * 1000000ULL);

    // Конфігуруємо пробудження ext0 від PIR-датчика за високим рівнем (1)
    rtc_gpio_pullup_dis(PIR_GPIO_NUM);
    rtc_gpio_pulldown_en(PIR_GPIO_NUM);
    esp_sleep_enable_ext0_wakeup(PIR_GPIO_NUM, 1);

    // Ізолюємо критичні виводи від витоків струму перед зануренням у сон
    rtc_gpio_isolate(GPIO_NUM_4);

    ESP_LOGI(TAG, "Перехід у режим Deep Sleep...");
    esp_deep_sleep_start();
}
