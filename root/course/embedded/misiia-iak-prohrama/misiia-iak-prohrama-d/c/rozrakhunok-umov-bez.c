#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef enum {
    COND_NONE,
    COND_WAIT_DELAY,
    COND_WAIT_DISTANCE,
    COND_WAIT_BATTERY
} condition_type_t;

typedef struct {
    condition_type_t type;
    uint32_t         start_timestamp_ms;
    uint32_t         target_duration_ms;
    float            target_distance_m;
    float            min_battery_soc_pct;
} active_condition_t;

bool evaluate_condition_tick(const active_condition_t *cond,
                             uint32_t current_time_ms,
                             float current_dist_m,
                             float current_battery_pct)
{
    switch (cond->type) {
        case COND_WAIT_DELAY:
            return (current_time_ms - cond->start_timestamp_ms) >= cond->target_duration_ms;

        case COND_WAIT_DISTANCE:
            return (current_dist_m <= cond->target_distance_m);

        case COND_WAIT_BATTERY:
            return (current_battery_pct < cond->min_battery_soc_pct);

        case COND_NONE:
        default:
            return true;
    }
}
