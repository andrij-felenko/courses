#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_RELAY  GPIO_NUM_25
#define RELAY_ON   0
#define RELAY_OFF  1

// Стан таймера реле.
static bool    relay_active = false;   // чи реле зараз увімкнене таймером
static int64_t relay_off_at = 0;       // МИТЬ (мс від старту), коли треба вимкнути

// 64-бітні мікросекунди → мілісекунди; такий лічильник не переповниться ніколи.
static int64_t now_ms(void) { return esp_timer_get_time() / 1000; }

// Увімкнути реле рівно на duration_ms мілісекунд.
void relay_on_for(int64_t duration_ms) {
    gpio_set_level(PIN_RELAY, RELAY_ON);
    relay_active = true;
    relay_off_at = now_ms() + duration_ms;   // коли гасити
}

// Викликати В КОЖНОМУ проході циклу: сам вимкне, коли час вийде.
void relay_tick(void) {
    if (relay_active && now_ms() >= relay_off_at) {
        gpio_set_level(PIN_RELAY, RELAY_OFF);
        relay_active = false;
    }
}

void app_main(void) {
    gpio_set_level(PIN_RELAY, RELAY_OFF);
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_RELAY, .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    relay_on_for(5000);               // клацнули увімкнене на 5 секунд

    while (1) {
        relay_tick();                 // стежить за часом, не блокуючи
        vTaskDelay(pdMS_TO_TICKS(10));   // віддаємо процесор іншим задачам
    }
}
