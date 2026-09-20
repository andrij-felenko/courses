#include <stdint.h>
#include <stdbool.h>

#define DEBOUNCE_MS 15
#define INVALID_POSITION 0xFF

typedef struct {
    uint16_t gpio_mask;
    uint8_t current_position;
    uint8_t pending_position;
    uint32_t stable_ticks;
} rotary_gpio_driver_t;

uint8_t decode_raw_gpio(uint16_t gpio_state) {
    for (uint8_t i = 0; i < 12; i++) {
        if ((gpio_state & (1 << i)) == 0) { // Активний низький рівень
            return i;
        }
    }
    return INVALID_POSITION; // BBM плаваючий стан
}

uint8_t rotary_filter_update(rotary_gpio_driver_t *driver, uint16_t raw_gpio_state, uint32_t dt_ms) {
    uint8_t detected = decode_raw_gpio(raw_gpio_state);
    
    if (detected == INVALID_POSITION || detected == driver->current_position) {
        driver->pending_position = driver->current_position;
        driver->stable_ticks = 0;
        return driver->current_position;
    }
    
    if (detected == driver->pending_position) {
        driver->stable_ticks += dt_ms;
        if (driver->stable_ticks >= DEBOUNCE_MS) {
            driver->current_position = detected;
            driver->stable_ticks = 0;
        }
    } else {
        driver->pending_position = detected;
        driver->stable_ticks = 0;
    }
    
    return driver->current_position;
}
