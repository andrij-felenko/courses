#include "esp_system.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

#define RTC_MAGIC            0xB007C0DEu   // "boot code" — вартовий лічильника
#define FAULT_THRESHOLD      5u            // патологічних рестартів за вікно
#define STABILITY_TIMEOUT_MS 60000u        // 60 с спокою → лічильник у нуль

static const char *TAG = "reboot";

// .rtc_noinit — завантажувач НЕ занулює; переживає Core Reset (wdt/panic/sw)
RTC_NOINIT_ATTR static uint32_t s_magic;
RTC_NOINIT_ATTR static uint32_t s_boot_fail_cnt;
static TimerHandle_t s_stability_timer;

static void stability_timer_cb(TimerHandle_t t) {
    ESP_LOGI(TAG, "stable for %u ms — clearing fault counter", STABILITY_TIMEOUT_MS);
    s_boot_fail_cnt = 0;            // вижили хвилину — починаємо лік спочатку
}

void startup_check(void) {
    esp_reset_reason_t reason = esp_reset_reason();

    // 1. Після System Reset (power-on/brown-out) у RTC_NOINIT лежить сміття.
    //    Вартовий-сигнатура каже, чи можна вірити лічильнику.
    if (s_magic != RTC_MAGIC || reason == ESP_RST_POWERON) {
        s_magic = RTC_MAGIC;
        s_boot_fail_cnt = 0;
    }

    // 2. Рахуємо лише патологічні причини: зависання й паніку.
    bool pathological = (reason == ESP_RST_TASK_WDT ||
                         reason == ESP_RST_INT_WDT  ||
                         reason == ESP_RST_PANIC);
    if (pathological) {
        s_boot_fail_cnt++;
        ESP_LOGW(TAG, "pathological reset (%d), fail_cnt=%u",
                 reason, s_boot_fail_cnt);
    }

    // 3. Поріг перейдено — лізти драбиною ескалації, а не падати знову.
    if (s_boot_fail_cnt >= FAULT_THRESHOLD) {
        ESP_LOGE(TAG, "boot loop! cnt=%u — escalating", s_boot_fail_cnt);
        if (!config_rollback_if_available()) {       // спершу відкат конфігу
            esp_ota_mark_app_invalid_rollback_and_reboot();  // тоді — прошивки
            // якщо й це не вернуло — лишаємось у safe mode назавжди
        }
        enter_safe_mode();                            // мінімальна конфігурація
        return;
    }

    // 4. Нормальний старт: завести таймер, що обнулить лічильник за хвилину.
    s_stability_timer = xTimerCreate("stab", pdMS_TO_TICKS(STABILITY_TIMEOUT_MS),
                                     pdFALSE, NULL, stability_timer_cb);
    xTimerStart(s_stability_timer, 0);
    // ... далі звичайна ініціалізація підсистем
}
