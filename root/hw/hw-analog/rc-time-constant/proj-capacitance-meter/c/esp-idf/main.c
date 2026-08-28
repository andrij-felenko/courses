#include "driver/gpio.h"
#include "esp_timer.h"
// esp_timer_get_time() — вільний 64-бітний лічильник мікросекунд від старту.

float measure_capacitance(float R_ohms) {
    static int64_t discharge_us = 200000;    // щедрий старт на перший цикл

    gpio_config_t io = { .pin_bit_mask = 1ULL << PIN_DRIVE, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&io);
    io.pin_bit_mask = 1ULL << PIN_SENSE; io.mode = GPIO_MODE_INPUT;
    gpio_config(&io);

    gpio_set_level(PIN_DRIVE, 0);            // 1. розряд крізь R
    int64_t d0 = esp_timer_get_time();
    while (esp_timer_get_time() - d0 < discharge_us) { /* поки не сяде до ~0 */ }

    int64_t t0 = esp_timer_get_time();
    gpio_set_level(PIN_DRIVE, 1);            // 2. старт заряду й таймера воднораз

    while (gpio_get_level(PIN_SENSE) == 0) { } // 3. чекаємо перетину порога V₀/2
    int64_t t_us = esp_timer_get_time() - t0;  //    тривалість заряду ≈ 0.69·τ

    discharge_us = 8 * t_us;                 // наступний розряд: 8·0.69τ ≈ 5.5τ ≥ 5τ
    return (t_us * 1e-6f) / (0.693f * R_ohms); // 4. ділимо на k·R → фаради
}
