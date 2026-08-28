#include "esp_sleep.h"
#include "driver/rtc_io.h"

#define PIN_PIR       GPIO_NUM_33     // OUT давача — на RTC-здатну ногу
RTC_DATA_ATTR uint32_t boot_count = 0;   // переживає сон у RTC-пам'яті

void setup() {
    Serial.begin(115200);
    delay(200);
    boot_count++;

    // Чому прокинулися?
    esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
    if (cause == ESP_SLEEP_WAKEUP_EXT0) {
        Serial.printf("Прокинувся від РУХУ. Пробудження #%u\n", boot_count);
        // --- корисна робота: надіслати сповіщення, зробити кадр, тощо ---
        do_useful_work();
    } else {
        // Перший старт (не від руху): дати давачу прогрітися перед сном.
        Serial.println("Холодний старт — прогрів давача 60 с");
        delay(60000);   // тут блокувати можна: нам однаково нічого не робити
    }

    // Налаштувати пробудження по фронту OUT і заснути.
    rtc_gpio_pulldown_en(PIN_PIR);          // тримати ногу в "0" під час сну
    rtc_gpio_pullup_dis(PIN_PIR);
    esp_sleep_enable_ext0_wakeup(PIN_PIR, 1);  // 1 = будити, коли нога стане HIGH

    Serial.println("Засинаю. Розбудить рух.");
    Serial.flush();
    esp_deep_sleep_start();      // все нижче не виконається — після пробудження setup() почнеться заново
}

void loop() { }   // при глибокому сні не використовується: після сну виконується setup()

void do_useful_work() {
    // місце для вашої логіки; має завершитися швидко, щоб знову заснути
    delay(500);
}
