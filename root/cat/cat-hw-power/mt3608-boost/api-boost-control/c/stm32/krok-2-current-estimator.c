/* ============================================================================
   krok-2-current-estimator.c — STM32 HAL: перевірка безпеки струму котушки
   ========================================================================== */

#include "main.h"

uint8_t MT3608_Check_Current_Limit(uint32_t vin_mv, uint32_t vout_mv, uint32_t i_out_ma) {
    if (vout_mv <= vin_mv) return 1;

    // Розрахунок D
    float d = 1.0f - ((float)vin_mv / (float)vout_mv);
    float i_in_est = (float)i_out_ma / ((1.0f - d) * 0.88f);

    if (i_in_est > 1800.0f) {
        return 0; // Перевантаження: струм перевищує 1.8 А
    }
    return 1;
}
