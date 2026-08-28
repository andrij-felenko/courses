#include <stdint.h>

// Усе в цілих: струми — мкА, час — секунди, ємність — мкА·год.
// Середній струм (мкА) для дводстанового циклу сон/активність.
static inline uint32_t avg_current_ua(uint32_t i_sleep_ua, uint32_t i_act_ua,
                                      uint32_t t_act_ms, uint32_t period_ms) {
    // I_avg = I_sleep + (I_act - I_sleep) * t_act / T
    uint64_t extra = (uint64_t)(i_act_ua - i_sleep_ua) * t_act_ms / period_ms;
    return i_sleep_ua + (uint32_t)extra;
}

// Прогноз життя в годинах від ЕФЕКТИВНОЇ ємності (мкА·год) і повного струму.
static inline uint32_t life_hours(uint32_t q_eff_uah, uint32_t i_total_ua) {
    return i_total_ua ? q_eff_uah / i_total_ua : 0;
}

// Приклад використання:
//   uint32_t iavg = avg_current_ua(12, 130000, 250, 60000);   // ≈ 554 мкА
//   uint32_t qeff = (uint32_t)(3000ull * 1000 * 85 * 80 / 10000); // мкА·год
//   uint32_t h    = life_hours(qeff, iavg + 3);  // + саморозряд ≈ 3 мкА → ≈ 3650 год
