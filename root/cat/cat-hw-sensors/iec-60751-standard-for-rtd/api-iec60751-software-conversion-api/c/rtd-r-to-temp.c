/* Реалізація прямого та оберненого перетворення на мові C */
#include "rtd_api.h"
#include <math.h>

rtd_status_t rtd_r_to_temp(const rtd_config_t *config, double r_meas, double *temp_out) {
    if (!config || !temp_out) return RTD_ERR_INVALID_PARAM;
    if (r_meas > config->r_max) return RTD_ERR_OPEN_CIRCUIT;
    if (r_meas < config->r_min) return RTD_ERR_SHORT_CIRCUIT;

    double r0 = config->r0;
    double A = config->coeff.A;
    double B = config->coeff.B;
    double C = config->coeff.C;

    /* Початкова оцінка за квадратичною формулою (t >= 0 °C) */
    double discriminant = A * A - 4.0 * B * (1.0 - r_meas / r0);
    if (discriminant < 0.0) return RTD_ERR_OUT_OF_RANGE;

    double temp = (-A + sqrt(discriminant)) / (2.0 * B);

    /* Якщо температура від'ємна, уточнюємо методом Ньютона — Рафсона */
    if (temp < 0.0) {
        for (int i = 0; i < 4; ++i) {
            double t2 = temp * temp;
            double t3 = t2 * temp;
            double f = r0 * (1.0 + A * temp + B * t2 + C * (temp - 100.0) * t3) - r_meas;
            double f_prime = r0 * (A + 2.0 * B * temp + C * (4.0 * t3 - 300.0 * t2));
            double delta = f / f_prime;
            temp -= delta;
            if (fabs(delta) < 1e-5) break;
        }
    }

    *temp_out = temp;
    return RTD_OK;
}

rtd_status_t rtd_temp_to_r(const rtd_config_t *config, double temp, double *r_out) {
    if (!config || !r_out) return RTD_ERR_INVALID_PARAM;
    if (temp < -200.0 || temp > 850.0) return RTD_ERR_OUT_OF_RANGE;

    double r0 = config->r0;
    double A = config->coeff.A;
    double B = config->coeff.B;
    double C = config->coeff.C;
    double r = 0.0;

    if (temp >= 0.0) {
        r = r0 * (1.0 + A * temp + B * temp * temp);
    } else {
        double t2 = temp * temp;
        double t3 = t2 * temp;
        r = r0 * (1.0 + A * temp + B * t2 + C * (temp - 100.0) * t3);
    }

    *r_out = r;
    return RTD_OK;
}
