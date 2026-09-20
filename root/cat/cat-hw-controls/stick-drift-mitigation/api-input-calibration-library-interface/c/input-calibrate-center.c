input_error_t input_calibrate_center(uint16_t raw_x, uint16_t raw_y, input_profile_t *profile) {
    if (profile == NULL) {
        return INPUT_ERR_INVALID_PARAM;
    }
    profile->axis_x.adc_center = raw_x;
    profile->axis_y.adc_center = raw_y;
    profile->axis_x.deadzone_inner = 0.05f;
    profile->axis_y.deadzone_inner = 0.05f;
    return INPUT_OK;
}

input_error_t input_calibrate_limits(uint16_t raw_x_min, uint16_t raw_x_max,
                                       uint16_t raw_y_min, uint16_t raw_y_max,
                                       input_profile_t *profile) {
    if (profile == NULL || raw_x_min >= raw_x_max || raw_y_min >= raw_y_max) {
        return INPUT_ERR_INVALID_PARAM;
    }
    profile->axis_x.adc_min = raw_x_min;
    profile->axis_x.adc_max = raw_x_max;
    profile->axis_y.adc_min = raw_y_min;
    profile->axis_y.adc_max = raw_y_max;
    return INPUT_OK;
}
