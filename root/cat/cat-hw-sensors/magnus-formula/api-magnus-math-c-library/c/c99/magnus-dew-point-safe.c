// Коди статусу виконання обчислювальних функцій
typedef enum {
    MAGNUS_OK = 0,
    MAGNUS_ERR_NULL_POINTER,
    MAGNUS_ERR_RH_OUT_OF_RANGE,
    MAGNUS_ERR_TEMP_OUT_OF_RANGE,
    MAGNUS_ERR_MATH_DOMAIN
} magnus_status_t;

// Валідована функція розрахунку точки роси для float32
magnus_status_t magnus_dew_point_safe(float temp, float rh, const magnus_params_t *params, float *out_dew_point) {
    if (params == NULL || out_dew_point == NULL) {
        return MAGNUS_ERR_NULL_POINTER;
    }
    if (rh <= 0.0f || rh > 100.0f) {
        return MAGNUS_ERR_RH_OUT_OF_RANGE;
    }
    if (temp < -50.0f || temp > 100.0f) {
        return MAGNUS_ERR_TEMP_OUT_OF_RANGE;
    }

    float gamma = logf(rh / 100.0f) + (params->b * temp) / (params->c + temp);
    float denom = params->b - gamma;

    if (denom == 0.0f) {
        return MAGNUS_ERR_MATH_DOMAIN;
    }

    *out_dew_point = (params->c * gamma) / denom;
    return MAGNUS_OK;
}
