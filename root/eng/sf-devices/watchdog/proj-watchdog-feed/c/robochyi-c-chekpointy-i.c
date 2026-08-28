#include "esp_task_wdt.h"
#include "esp_timer.h"          // esp_timer_get_time() — мікросекунди від старту
#include <stdint.h>
#include <stdbool.h>

#define TASK_COUNT 3

// останній успішний оберт кожної задачі (мс) і її дозволений строк (мс)
static volatile uint32_t last_ok[TASK_COUNT];
static const    uint32_t deadline_ms[TASK_COUNT] = { 200, 2000, 300000 };

static inline uint32_t now_ms(void) {
    return (uint32_t)(esp_timer_get_time() / 1000);   // мкс → мс
}

// кожна задача кличе це, завершивши УСПІШНИЙ оберт:
void checkpoint(int task_id) {
    last_ok[task_id] = now_ms();
}

// збирач: годуємо watchdog ЛИШЕ якщо всі задачі свіжі
void watchdog_collect(void) {
    uint32_t t = now_ms();
    for (int i = 0; i < TASK_COUNT; i++) {
        if (t - last_ok[i] > deadline_ms[i]) {
            return;                  // ця задача протухла → НЕ годуємо
        }
    }
    esp_task_wdt_reset();            // усі свіжі → доказ поступу → годуємо
}
