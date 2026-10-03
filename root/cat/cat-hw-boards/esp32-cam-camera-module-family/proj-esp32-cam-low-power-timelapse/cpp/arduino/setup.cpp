#include <Arduino.h>
#include <esp_sleep.h>
#include <driver/rtc_io.h>

#define PIR_GPIO_NUM GPIO_NUM_13
#define TIME_TO_SLEEP_SEC 3600ULL

void setup() {
    Serial.begin(115200);
    delay(100);

    // Визначення причини виходу з режиму глибокого сну
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();

    if (wakeup_reason == ESP_SLEEP_WAKEUP_TIMER) {
        Serial.println("Таймер RTC: планова зйомка за розкладом");
    } else if (wakeup_reason == ESP_SLEEP_WAKEUP_EXT0) {
        Serial.println("Датчик PIR: виявлено рух, фіксація кадру");
    } else {
        Serial.println("Перший старт пристрою");
    }

    // Виконання процедури захоплення зображення та запису на microSD

    // Конфігурування періодичного пробудження RTC-таймера
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_SEC * 1000000ULL);

    // Налаштування зовнішього тригера ext0 на GPIO13 від PIR-сенсора
    rtc_gpio_pullup_dis((gpio_num_t)PIR_GPIO_NUM);
    rtc_gpio_pulldown_en((gpio_num_t)PIR_GPIO_NUM);
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIR_GPIO_NUM, 1);

    // Ізоляція сигнального виводу світлодіода спалаху
    rtc_gpio_isolate(GPIO_NUM_4);

    Serial.println("Занурення системи в Deep Sleep");
    Serial.flush();
    esp_deep_sleep_start();
}

void loop() {
    // Код не виконується, оскільки мікроконтролер перебуває у глибокому сні
}
