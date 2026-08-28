// ESP-IDF. Періодичний esp_timer будить задачу — крок відмірює залізо, не затримка.
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static SemaphoreHandle_t tick;              // прапорець «час знімка»
static esp_timer_handle_t sampler;

static void on_timer(void* arg) { xSemaphoreGive(tick); }   // коротко й без блокувань

void setup_sampler(uint32_t fs_hz) {
    tick = xSemaphoreCreateBinary();
    const esp_timer_create_args_t cfg = { .callback = on_timer, .name = "sampler" };
    ESP_ERROR_CHECK(esp_timer_create(&cfg, &sampler));
    ESP_ERROR_CHECK(esp_timer_start_periodic(sampler, 1000000ULL / fs_hz));  // період у мкс
}
