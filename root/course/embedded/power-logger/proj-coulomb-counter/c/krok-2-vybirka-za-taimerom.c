#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"

static accumulator_t g_acc;
static portMUX_TYPE  g_acc_lock = portMUX_INITIALIZER_UNLOCKED;
static int64_t       g_last_us;          // мітка часу попередньої вибірки

// Колбек періодичного таймера (контекст задачі esp_timer, не ISR).
static void sample_cb(void *arg) {
    int64_t now = esp_timer_get_time();          // мікросекунди від старту
    uint32_t dt = (uint32_t)(now - g_last_us);   // реальний інтервал, не номінальний!
    g_last_us = now;

    uint32_t i_uA = current_sensor_read_uA();    // блокувальне читання по I²C — тут можна

    taskENTER_CRITICAL(&g_acc_lock);
    acc_add_sample(&g_acc, i_uA, dt);
    taskEXIT_CRITICAL(&g_acc_lock);
}

void coulomb_counter_start(uint32_t period_ms) {
    g_last_us = esp_timer_get_time();
    const esp_timer_create_args_t args = {
        .callback = &sample_cb, .name = "coulomb"
    };
    esp_timer_handle_t h;
    esp_timer_create(&args, &h);
    esp_timer_start_periodic(h, (uint64_t)period_ms * 1000u);  // період у мкс
}
