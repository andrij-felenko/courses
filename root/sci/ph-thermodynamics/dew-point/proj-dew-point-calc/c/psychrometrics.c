/* psychrometrics.c — C99 реалізація */
#include "psychrometrics.h"
#include <math.h>

#define MAGNUS_A 0.61078
#define MAGNUS_B 17.27
#define MAGNUS_C 237.3

#define MAGNUS_ICE_B 21.875
#define MAGNUS_ICE_C 265.5

psychro_error_t psychro_calculate(double temp_c, double rh_pct, psychro_result_t *res) {
    if (!res) return PSYCHRO_ERR_NULL_POINTER;
    if (temp_c < -50.0 || temp_c > 80.0) return PSYCHRO_ERR_TEMP_OUT_OF_RANGE;
    if (rh_pct < 0.0 || rh_pct > 100.0) return PSYCHRO_ERR_HUMIDITY_OUT_OF_RANGE;

    res->air_temp_c = temp_c;
    res->rel_humidity_pct = rh_pct;

    /* Тиск насиченої пари p_sat(T) */
    res->sat_vapor_press_kpa = MAGNUS_A * exp((MAGNUS_B * temp_c) / (MAGNUS_C + temp_c));
    
    /* Парціальний тиск p_v */
    res->vapor_press_kpa = (rh_pct / 100.0) * res->sat_vapor_press_kpa;

    /* Обчислення точки роси T_d */
    if (rh_pct < 0.001) {
        res->dew_point_c = -50.0;
        res->frost_point_c = -50.0;
    } else {
        double alpha = ((MAGNUS_B * temp_c) / (MAGNUS_C + temp_c)) + log(rh_pct / 100.0);
        res->dew_point_c = (MAGNUS_C * alpha) / (MAGNUS_B - alpha);

        /* Точка інею над льодом */
        double alpha_ice = ((MAGNUS_ICE_B * temp_c) / (MAGNUS_ICE_C + temp_c)) + log(rh_pct / 100.0);
        res->frost_point_c = (MAGNUS_ICE_C * alpha_ice) / (MAGNUS_ICE_B - alpha_ice);
    }

    return PSYCHRO_OK;
}

bool anti_cond_update(anti_cond_controller_t *ctrl, double surface_temp_c, double dew_point_c) {
    if (!ctrl) return false;

    double margin = surface_temp_c - dew_point_c;

    if (margin <= ctrl->temp_margin_on_c) {
        ctrl->heater_active = true;
    } else if (margin >= ctrl->temp_margin_off_c) {
        ctrl->heater_active = false;
    }

    return ctrl->heater_active;
}
