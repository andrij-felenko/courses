#include "rtd_lut.h"
#include <stddef.h>
#include <stdint.h>

rtd_status_t rtd_lut_init(rtd_lut_t *lut, rtd_type_t type) {
    if (lut == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    if (type != RTD_TYPE_PT100 && type != RTD_TYPE_PT1000) {
        return RTD_ERROR_INVALID_TYPE;
    }

    rtd_config_t config;
    rtd_status_t status = rtd_init(&config, type, RTD_CLASS_B);
    if (status != RTD_SUCCESS) {
        return status;
    }

    lut->type = type;
    lut->min_temp_mc = RTD_LUT_MIN_TEMP * 1000;
    lut->step_temp_mc = RTD_LUT_STEP_DEG * 1000;
    lut->size = RTD_LUT_ELEMENT_COUNT;

    for (size_t i = 0; i < lut->size; i++) {
        double temp_c = (double)RTD_LUT_MIN_TEMP + (double)i * (double)RTD_LUT_STEP_DEG;
        double res_ohm;
        rtd_temperature_to_resistance(&config, temp_c, &res_ohm);
        /* Перетворення опору в міліоми з округленням до найближчого цілого */
        lut->resistance_mohm[i] = (uint32_t)(res_ohm * 1000.0 + 0.5);
    }

    return RTD_SUCCESS;
}

rtd_status_t rtd_lut_lookup_temp_mc(const rtd_lut_t *lut, uint32_t resistance_mohm, int32_t *temp_mc) {
    if (lut == NULL || temp_mc == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    if (resistance_mohm < lut->resistance_mohm[0] ||
        resistance_mohm > lut->resistance_mohm[lut->size - 1]) {
        return RTD_ERROR_OUT_OF_RANGE;
    }

    /* Двохточковий двоінтервальний бінарний пошук для знаходження потрібного сегмента */
    size_t low = 0;
    size_t high = lut->size - 1;

    while (low < high - 1) {
        size_t mid = low + (high - low) / 2;
        if (lut->resistance_mohm[mid] <= resistance_mohm) {
            low = mid;
        } else {
            high = mid;
        }
    }

    uint32_t r_low = lut->resistance_mohm[low];
    uint32_t r_high = lut->resistance_mohm[low + 1];

    int32_t t_low_mc = lut->min_temp_mc + (int32_t)low * lut->step_temp_mc;

    uint32_t delta_r = r_high - r_low;
    if (delta_r == 0) {
        *temp_mc = t_low_mc;
        return RTD_SUCCESS;
    }

    uint32_t delta_meas = resistance_mohm - r_low;

    /* Цілочисельна лінійна інтерполяція з округленням:
       T_mc = T_low_mc + (delta_meas * step_temp_mc + delta_r / 2) / delta_r */
    int64_t numerator = (int64_t)delta_meas * (int64_t)lut->step_temp_mc;
    int32_t interp_mc = (int32_t)((numerator + (delta_r / 2)) / delta_r);

    *temp_mc = t_low_mc + interp_mc;
    return RTD_SUCCESS;
}

rtd_status_t rtd_lut_lookup_temp_c(const rtd_lut_t *lut, double resistance_ohm, double *temp_c) {
    if (lut == NULL || temp_c == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    uint32_t res_mohm = (uint32_t)(resistance_ohm * 1000.0 + 0.5);
    int32_t t_mc;
    rtd_status_t status = rtd_lut_lookup_temp_mc(lut, res_mohm, &t_mc);

    if (status == RTD_SUCCESS) {
        *temp_c = (double)t_mc / 1000.0;
    }

    return status;
}
