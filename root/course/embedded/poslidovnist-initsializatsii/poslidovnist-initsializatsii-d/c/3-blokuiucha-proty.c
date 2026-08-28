#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t power_on_timestamp;
    bool power_stable;
} sensor_power_guard_t;

void sensor_start_power_timer(sensor_power_guard_t *guard) {
    hw_power_rail_enable(true);
    guard->power_on_timestamp = platform_get_millis();
    guard->power_stable = false;
}

bool sensor_is_power_ready(sensor_power_guard_t *guard, uint32_t required_boot_ms) {
    if (guard->power_stable) {
        return true;
    }
    uint32_t now = platform_get_millis();
    /* Обробка переповнення лічильника мілісекунд (32-бітний беззнаковий розрахунок) */
    if ((now - guard->power_on_timestamp) >= required_boot_ms) {
        guard->power_stable = true;
        return true;
    }
    return false;
}
