#include "esp_timer.h"

static uint32_t last_event  = 0;   // мітка часу останньої зарахованої події, мс
static uint32_t sound_count = 0;   // лічильник гучних подій
#define WINDOW_MS  300             // мертва зона після події

static inline uint32_t millis_now(void) {          // вільно біжний лічильник мілісекунд
    return (uint32_t)(esp_timer_get_time() / 1000);
}

void ky038_task(void *arg) {
    bool was_sound = false;                        // чи був звук у попередній ітерації
    for (;;) {
        bool is_sound = (gpio_get_level(PIN_DO) != idle_level);   // звук = «не спокій»

        // цікавить саме ФРОНТ: тиша щойно змінилася на звук
        if (is_sound && !was_sound) {
            uint32_t now = millis_now();
            if (now - last_event > WINDOW_MS) {     // і вікно вже минуло
                last_event = now;
                sound_count++;
                ESP_LOGI(TAG, "подія #%lu", (unsigned long)sound_count);
            }
        }
        was_sound = is_sound;

        vTaskDelay(pdMS_TO_TICKS(2));   // віддаємо процесор іншим задачам — не блокуємось
    }
}
