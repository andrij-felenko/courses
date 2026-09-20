#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_timer.h"

// Структура конфігурації та стану двоканального входу
typedef struct {
    gpio_num_t pin_a;             // GPIO вивід Каналу A
    gpio_num_t pin_b;             // GPIO вивід Каналу B
    bool state_a;                 // Відфільтрований стан Каналу A
    bool state_b;                 // Відфільтрований стан Каналу B
    bool raw_a;                   // Сирий поточний рівень A
    bool raw_b;                   // Сирий поточний рівень B
    uint64_t last_debounce_time_a;// Часова мітка зміни A (мікросекунди)
    uint64_t last_debounce_time_b;// Часова мітка зміни B (мікросекунди)
    uint32_t debounce_delay_us;   // Затримка фільтрації (мікросекунди)
} enabling_switch_hw_t;

// Неблокуюче зчитування та фільтрація брязкоту
void enabling_switch_update_hw(enabling_switch_hw_t *hw) {
    uint64_t now = esp_timer_get_time();
    bool sample_a = gpio_get_level(hw->pin_a);
    bool sample_b = gpio_get_level(hw->pin_b);

    if (sample_a != hw->raw_a) {
        hw->raw_a = sample_a;
        hw->last_debounce_time_a = now;
    }
    if ((now - hw->last_debounce_time_a) > hw->debounce_delay_us) {
        hw->state_a = hw->raw_a;
    }

    if (sample_b != hw->raw_b) {
        hw->raw_b = sample_b;
        hw->last_debounce_time_b = now;
    }
    if ((now - hw->last_debounce_time_b) > hw->debounce_delay_us) {
        hw->state_b = hw->raw_b;
    }
}
