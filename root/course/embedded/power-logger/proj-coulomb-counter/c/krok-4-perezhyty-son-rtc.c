#include "esp_sleep.h"

// Стан, що мусить пережити deep sleep. Живе в RTC slow memory.
RTC_DATA_ATTR static accumulator_t rtc_acc;        // незавершене вікно
RTC_DATA_ATTR static uint32_t      rtc_write_off;  // голова кільця
RTC_DATA_ATTR static uint32_t      rtc_seq;        // наступний номер запису
RTC_DATA_ATTR static uint32_t      rtc_magic;      // ознака валідності RTC-стану

#define RTC_MAGIC 0xC0FFEE01u

// Викликати на старті, ДО запуску лічильника.
void coulomb_counter_restore(void) {
    esp_reset_reason_t reason = esp_reset_reason();
    bool from_deep_sleep = (reason == ESP_RST_DEEPSLEEP);

    if (from_deep_sleep && rtc_magic == RTC_MAGIC) {
        // Теплий старт: RTC-памʼять валідна — продовжуємо точно з місця.
        g_acc       = rtc_acc;
        g_write_off = rtc_write_off;
        g_seq       = rtc_seq;
    } else {
        // Холодний старт: RTC-вмісту немає — відновлюємо голову з Flash.
        g_acc.window_pC = 0;
        g_acc.window_us = 0;
        ring_recover_head(&g_write_off, &g_seq);   // прохід по кільцю, нижче
        rtc_magic = RTC_MAGIC;
    }
}

// Викликати безпосередньо перед esp_deep_sleep_start().
void coulomb_counter_persist(void) {
    taskENTER_CRITICAL(&g_acc_lock);
    rtc_acc = g_acc;            // незавершений заряд вікна — у RTC, не загубиться
    taskEXIT_CRITICAL(&g_acc_lock);
    rtc_write_off = g_write_off;
    rtc_seq       = g_seq;
    rtc_magic     = RTC_MAGIC;
}
