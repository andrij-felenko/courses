#include <stdint.h>

/**
 * @brief Цілочисельний розрахунок фізичних параметрів
 */
void calculate_fixed_point(uint16_t vrefint_cal,
                           uint16_t ts_cal1,
                           uint16_t ts_cal2,
                           uint16_t raw_vrefint,
                           uint16_t raw_ts,
                           uint16_t raw_channel,
                           uint32_t *out_vdda_mv,
                           int32_t  *out_temp_01c,
                           uint32_t *out_channel_mv) {
    if (raw_vrefint == 0) return;

    /* 1. Розрахунок VDDA в мВ з математичним округленням */
    uint32_t vdda_mv = ((uint32_t)3000 * vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;
    *out_vdda_mv = vdda_mv;

    /* 2. Нормалізація коду термодатчика до напруги 3.0 В */
    uint32_t ts_norm = ((uint32_t)raw_ts * vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;

    /* 3. Розрахунок температури в десятих частках °C (0.1 °C) */
    int32_t delta_cal = (int32_t)ts_cal2 - (int32_t)ts_cal1;
    if (delta_cal != 0) {
        int32_t temp_01c = ((int32_t)(ts_norm - ts_cal1) * 1000 + (delta_cal / 2)) / delta_cal + 300;
        *out_temp_01c = temp_01c;
    }

    /* 4. Відновлення напруги зовнішнього входу в мВ */
    uint32_t vin_mv = (vdda_mv * (uint32_t)raw_channel + 2047U) / 4095U;
    *out_channel_mv = vin_mv;
}
