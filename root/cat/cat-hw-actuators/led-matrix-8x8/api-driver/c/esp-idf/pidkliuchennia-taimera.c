#include "esp_timer.h"

// Це і є та функція, яку таймер смикає 1000 разів на секунду.
static void scanTimerCb(void *arg) {
    scanStep();
}

static void setupScanTimer(void) {
    const esp_timer_create_args_t args = {
        .callback = &scanTimerCb,
        .arg      = NULL,
        .name     = "scan",
    };
    esp_timer_handle_t h;
    ESP_ERROR_CHECK(esp_timer_create(&args, &h));
    // Передільники рахувати не треба: період задають у мікросекундах.
    // 1000 мкс → рівно 1000 переривань за секунду.
    ESP_ERROR_CHECK(esp_timer_start_periodic(h, 1000));
}
