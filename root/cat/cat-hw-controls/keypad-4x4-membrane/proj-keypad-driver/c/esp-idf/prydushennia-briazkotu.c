#include "esp_timer.h"
#include "esp_log.h"
#include <stdbool.h>

// антидеренч однієї клавіші на «таймері краю»:
#define DEBOUNCE_US (20 * 1000)   // 20 мс у мікросекундах
static const char *TAG = "keypad";

static bool    last_raw = false;  // сирий стан минулого разу
static bool    stable   = false;  // стан, якому вже віримо
static int64_t t_edge   = 0;      // коли рівень востаннє смикнувся
static bool    reported = false;  // чи вже повідомили про це натискання

// raw — сирий результат сканування цієї клавіші (true = замкнено)
void debounce_key(bool raw) {
    int64_t now = esp_timer_get_time();   // мікросекунди від старту, монотонні
    if (raw != last_raw) {                // рівень щойно змінився — перезапустити відлік
        t_edge = now;
        last_raw = raw;
    }
    if (now - t_edge >= DEBOUNCE_US) {    // протримався досить довго — вірити
        stable = raw;
    }
    if (stable && !reported) {            // стійке замикання, ще не повідомляли
        ESP_LOGI(TAG, "натиск (свій антидеренч)");
        reported = true;                  // одна подія на натискання
    }
    if (!stable) reported = false;        // клавіша відпустилась — готові до нового
}
