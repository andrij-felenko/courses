#include "deadline.h"

#include <math.h>

uint32_t esc_deadline_ms(float distance_to_obstacle_m,
                         float current_speed_mps,
                         float max_braking_decel_mps2,
                         float safety_margin_m,
                         uint32_t sensor_lag_ms)
{
    /* NaN від сенсора або від'ємна дистанція — поводимося як у найгіршому випадку */
    if (!isfinite(distance_to_obstacle_m) || !isfinite(current_speed_mps) ||
        !isfinite(max_braking_decel_mps2) || !isfinite(safety_margin_m)) {
        return 0u;
    }
    if (max_braking_decel_mps2 <= 0.05f) {
        return 0u;  /* гальм фактично немає — рішення не відкладаємо */
    }
    if (current_speed_mps < 0.1f) {
        return ESC_DEADLINE_IDLE_MS;  /* стоїмо: часу вдосталь, але не безкінечно */
    }
    if (distance_to_obstacle_m <= 0.0f) {
        return 0u;
    }

    /* Гальмівний шлях S = V^2 / (2a) плюс обов'язковий запас */
    const float braking_m   = (current_speed_mps * current_speed_mps) / (2.0f * max_braking_decel_mps2);
    const float safe_m      = braking_m + safety_margin_m;
    if (distance_to_obstacle_m <= safe_m) {
        return 0u;  /* уже в зоні екстреного гальмування */
    }

    const float free_m   = distance_to_obstacle_m - safe_m;
    const float free_sec = free_m / current_speed_mps;
    if (free_sec >= 60.0f) {
        return ESC_DEADLINE_MAX_MS;  /* захист від переповнення при мізерній швидкості */
    }

    uint32_t free_ms = (uint32_t)(free_sec * 1000.0f);
    /* Латентність тракту: кадр, інференс, радіо туди й назад — цей час уже витрачено */
    if (free_ms <= sensor_lag_ms) {
        return 0u;
    }
    free_ms -= sensor_lag_ms;

    return (free_ms > ESC_DEADLINE_MAX_MS) ? ESC_DEADLINE_MAX_MS : free_ms;
}
