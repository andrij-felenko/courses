#include "rtd_iec60751.h"
#include <math.h>
#include <stddef.h>
#include <stdbool.h>

rtd_status_t rtd_init(rtd_config_t *config, rtd_type_t type, rtd_class_t tolerance_class) {
    if (config == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    if (type != RTD_TYPE_PT100 && type != RTD_TYPE_PT1000) {
        return RTD_ERROR_INVALID_TYPE;
    }

    if (tolerance_class < RTD_CLASS_AA || tolerance_class > RTD_CLASS_C) {
        return RTD_ERROR_INVALID_CLASS;
    }

    config->type = type;
    config->tolerance = tolerance_class;
    config->r0 = (type == RTD_TYPE_PT100) ? RTD_PT100_R0 : RTD_PT1000_R0;

    return RTD_SUCCESS;
}

rtd_status_t rtd_temperature_to_resistance(const rtd_config_t *config, double temp_c, double *resistance) {
    if (config == NULL || resistance == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    if (temp_c < RTD_TEMP_MIN || temp_c > RTD_TEMP_MAX) {
        return RTD_ERROR_OUT_OF_RANGE;
    }

    double r;
    if (temp_c >= 0.0) {
        /* Для додатних температур: R(t) = R0 * (1 + A*t + B*t^2) */
        r = config->r0 * (1.0 + RTD_CVD_A * temp_c + RTD_CVD_B * temp_c * temp_c);
    } else {
        /* Для від'ємних температур: R(t) = R0 * (1 + A*t + B*t^2 + C*(t - 100)*t^3) */
        double t2 = temp_c * temp_c;
        double t3 = t2 * temp_c;
        r = config->r0 * (1.0 + RTD_CVD_A * temp_c + RTD_CVD_B * t2 + RTD_CVD_C * (temp_c - 100.0) * t3);
    }

    *resistance = r;
    return RTD_SUCCESS;
}

rtd_status_t rtd_resistance_to_temperature_nr(const rtd_config_t *config,
                                              double resistance,
                                              double max_error_c,
                                              size_t max_iterations,
                                              double *temp_c,
                                              size_t *iterations_used) {
    if (config == NULL || temp_c == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    /* Визначення крайніх межевих опорів при -200 °C та +850 °C */
    double min_res, max_res;
    rtd_temperature_to_resistance(config, RTD_TEMP_MIN, &min_res);
    rtd_temperature_to_resistance(config, RTD_TEMP_MAX, &max_res);

    if (resistance < min_res || resistance > max_res) {
        return RTD_ERROR_OUT_OF_RANGE;
    }

    /* Початкове наближення за лінійною моделью */
    double t = (resistance / config->r0 - 1.0) / RTD_CVD_A;
    size_t iter = 0;
    bool converged = false;

    while (iter < max_iterations) {
        double f, df;

        if (t >= 0.0) {
            /* Функція: f(t) = R0 * (1 + A*t + B*t^2) - R_meas */
            /* Похідна: df/dt = R0 * (A + 2*B*t) */
            f = config->r0 * (1.0 + RTD_CVD_A * t + RTD_CVD_B * t * t) - resistance;
            df = config->r0 * (RTD_CVD_A + 2.0 * RTD_CVD_B * t);
        } else {
            /* Розкрите рівняння для від'ємних температур: */
            /* f(t) = R0 * (1 + A*t + B*t^2 + C*t^4 - 100*C*t^3) - R_meas */
            /* Похідна: df/dt = R0 * (A + 2*B*t + 4*C*t^3 - 300*C*t^2) */
            double t2 = t * t;
            double t3 = t2 * t;
            double t4 = t3 * t;
            f = config->r0 * (1.0 + RTD_CVD_A * t + RTD_CVD_B * t2 + RTD_CVD_C * (t4 - 100.0 * t3)) - resistance;
            df = config->r0 * (RTD_CVD_A + 2.0 * RTD_CVD_B * t + 4.0 * RTD_CVD_C * t3 - 300.0 * RTD_CVD_C * t2);
        }

        if (fabs(df) < 1e-12) {
            return RTD_ERROR_CONVERGENCE_FAILED;
        }

        double delta = f / df;
        t -= delta;
        iter++;

        if (fabs(delta) < max_error_c) {
            converged = true;
            break;
        }
    }

    if (!converged) {
        return RTD_ERROR_CONVERGENCE_FAILED;
    }

    *temp_c = t;
    if (iterations_used != NULL) {
        *iterations_used = iter;
    }

    return RTD_SUCCESS;
}

rtd_status_t rtd_get_tolerance_c(rtd_class_t tolerance_class, double temp_c, double *tolerance_c) {
    if (tolerance_c == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    double abs_t = fabs(temp_c);
    switch (tolerance_class) {
        case RTD_CLASS_AA:
            *tolerance_c = 0.10 + 0.0017 * abs_t;
            break;
        case RTD_CLASS_A:
            *tolerance_c = 0.15 + 0.0020 * abs_t;
            break;
        case RTD_CLASS_B:
            *tolerance_c = 0.30 + 0.0050 * abs_t;
            break;
        case RTD_CLASS_C:
            *tolerance_c = 0.60 + 0.0100 * abs_t;
            break;
        default:
            return RTD_ERROR_INVALID_CLASS;
    }

    return RTD_SUCCESS;
}

rtd_status_t rtd_validate_tolerance(const rtd_config_t *config,
                                    double resistance,
                                    double temp_c,
                                    bool *is_valid,
                                    double *dev_c) {
    if (config == NULL || is_valid == NULL) {
        return RTD_ERROR_NULL_POINTER;
    }

    double calc_temp;
    rtd_status_t status = rtd_resistance_to_temperature_nr(config, resistance, 1e-5, 20, &calc_temp, NULL);
    if (status != RTD_SUCCESS) {
        return status;
    }

    double max_tol;
    status = rtd_get_tolerance_c(config->tolerance, temp_c, &max_tol);
    if (status != RTD_SUCCESS) {
        return status;
    }

    double deviation = calc_temp - temp_c;
    if (dev_c != NULL) {
        *dev_c = deviation;
    }

    *is_valid = (fabs(deviation) <= max_tol);
    return RTD_SUCCESS;
}
