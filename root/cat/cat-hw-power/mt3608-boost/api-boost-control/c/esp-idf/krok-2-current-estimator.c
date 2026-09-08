/* ============================================================================
   krok-2-current-estimator.c — ESP-IDF: оцінка струму індуктивності та захист
   ========================================================================== */

#include <stdio.h>
#include <stdbool.h>
#include "esp_log.h"

static const char *TAG = "BOOST_MATH";

#define MAX_INDUCTOR_CURRENT_MA  1800  // Запобігання насиченню ключа 2.0 А

/**
 * Розраховує вхідний струм від батареї за виміряними Vin, Vout та I_load
 */
bool check_boost_safety(uint32_t vin_mv, uint32_t vout_mv, uint32_t i_load_ma) {
    if (vin_mv == 0 || vout_mv <= vin_mv) return true;

    // Розрахунок коефіцієнта заповнення D = 1 - (Vin / Vout)
    float d = 1.0f - ((float)vin_mv / (float)vout_mv);

    // Оцінка вхідного струму I_in = I_out / ((1 - D) * ККД)
    const float efficiency = 0.88f;
    float estimated_in_current_ma = (float)i_load_ma / ((1.0f - d) * efficiency);

    if (estimated_in_current_ma > MAX_INDUCTOR_CURRENT_MA) {
        ESP_LOGE(TAG, "УВАГА: Небезпечний струм дроселя! Розрахунок: %.1f мА (ліміт %d мА)",
                 estimated_in_current_ma, MAX_INDUCTOR_CURRENT_MA);
        return false; // Потрібно збавити навантаження
    }

    return true; // Безпечний режим
}
