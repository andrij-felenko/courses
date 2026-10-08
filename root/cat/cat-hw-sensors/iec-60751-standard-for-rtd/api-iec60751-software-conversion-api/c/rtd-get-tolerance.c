/* Обчислення допусків та калібрування на мові C */
#include "rtd_api.h"
#include <math.h>

rtd_status_t rtd_get_tolerance(const rtd_config_t *config, double temp, double *tol_temp, double *tol_r) {
    if (!config || !tol_temp) return RTD_ERR_INVALID_PARAM;

    double abs_t = fabs(temp);
    double dt = 0.0;

    switch (config->accuracy_class) {
        case RTD_CLASS_AA: dt = 0.10 + 0.0017 * abs_t; break;
        case RTD_CLASS_A:  dt = 0.15 + 0.0020 * abs_t; break;
        case RTD_CLASS_B:  dt = 0.30 + 0.0050 * abs_t; break;
        case RTD_CLASS_C:  dt = 0.60 + 0.0100 * abs_t; break;
        default:           dt = 0.30 + 0.0050 * abs_t; break;
    }

    *tol_temp = dt;

    if (tol_r) {
        /* Обчислення похідної dR/dt для переведення °C в Ом */
        double dr_dt = config->r0 * (config->coeff.A + 2.0 * config->coeff.B * temp);
        *tol_r = dt * fabs(dr_dt);
    }

    return RTD_OK;
}
