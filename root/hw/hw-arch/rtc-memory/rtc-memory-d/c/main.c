#include "esp_sleep.h"
#include <string.h>

// Ці змінні живуть у RTC SLOW пам'яті — переживають deep-sleep
RTC_DATA_ATTR int   boot_count = 0;
RTC_DATA_ATTR float samples[6];
RTC_DATA_ATTR int   sample_idx = 0;

#define BATCH_SIZE 6
#define SLEEP_PERIOD_US (10ULL * 60 * 1000000)   // 10 хвилин

static float read_sensor(void) {
    // ... реальне зчитування ADC або I2C-давача ...
    return 22.5f;
}

static void send_batch(float *data, int count) {
    // ... підключення Wi-Fi, MQTT/HTTP, відключення ...
}

void app_main(void) {
    boot_count++;
    esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();

    if (cause == ESP_SLEEP_WAKEUP_UNDEFINED) {
        // Холодний старт — RTC-пам'ять містить сміття, ініціалізуємо
        sample_idx = 0;
        memset(samples, 0, sizeof(samples));
    }

    // Зчитати вимір і накопичити в RTC-пам'яті
    samples[sample_idx % BATCH_SIZE] = read_sensor();
    sample_idx++;

    // Кожне 6-те прокидання — віддати накопичене одним пакетом
    if (sample_idx % BATCH_SIZE == 0) {
        send_batch(samples, BATCH_SIZE);   // дорога Wi-Fi-фаза — раз на 60 хв
    }

    // Назад у deep-sleep — RTC-пам'ять збережена до наступного разу
    esp_sleep_enable_timer_wakeup(SLEEP_PERIOD_US);
    esp_deep_sleep_start();
}
