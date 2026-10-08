/* Комплексна обробка вимірювання та діагностика на мові C */
#include "rtd_api.h"

rtd_status_t rtd_process_measurement(const rtd_config_t *config, double r_meas, double i_meas_a, double *temp_out, double *tol_out) {
    if (!config || !temp_out) return RTD_ERR_INVALID_PARAM;

    /* 1. Контроль вимірювального струму для запобігання самонагріву */
    if (i_meas_a > config->max_current_a) {
        return RTD_ERR_SELF_HEATING;
    }

    /* 2. Контроль апаратних відмов лінії (обрив / коротке замикання) */
    if (r_meas >= config->r_max) {
        return RTD_ERR_OPEN_CIRCUIT;
    }
    if (r_meas <= config->r_min) {
        return RTD_ERR_SHORT_CIRCUIT;
    }

    /* 3. Лінеаризація та перетворення опору в температуру */
    rtd_status_t status = rtd_r_to_temp(config, r_meas, temp_out);
    if (status != RTD_OK) {
        return status;
    }

    /* 4. Обчислення допуску вимірювання */
    if (tol_out) {
        rtd_get_tolerance(config, *temp_out, tol_out, NULL);
    }

    return RTD_OK;
}
