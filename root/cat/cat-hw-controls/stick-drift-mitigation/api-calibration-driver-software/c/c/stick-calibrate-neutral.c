typedef struct {
    uint16_t raw_x_zero;
    uint16_t raw_y_zero;
    uint16_t raw_x_min;
    uint16_t raw_x_max;
    uint16_t raw_y_min;
    uint16_t raw_y_max;
    float deadzone_radial;
} stick_config_t;

typedef enum {
    STICK_OK = 0,
    STICK_ERR_NULL_PTR = -1,
    STICK_ERR_INVALID_CALIB = -2
} stick_err_t;

stick_err_t stick_calibrate_neutral(stick_config_t *cfg, const uint16_t *x_samples, const uint16_t *y_samples, size_t count) {
    if (!cfg || !x_samples || !y_samples || count == 0) return STICK_ERR_NULL_PTR;
    uint32_t sum_x = 0, sum_y = 0;
    for (size_t i = 0; i < count; i++) {
        sum_x += x_samples[i];
        sum_y += y_samples[i];
    }
    cfg->raw_x_zero = (uint16_t)(sum_x / count);
    cfg->raw_y_zero = (uint16_t)(sum_y / count);
    return STICK_OK;
}
