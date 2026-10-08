// Фіксація поточного положення як електричного нуля
lvdt_status_t lvdt_calibrate_zero(lvdt_handle_t *handle) {
    if (handle == NULL) {
        return LVDT_ERR_INVALID_PARAM;
    }
    handle->calibration.zero_offset_ratio = handle->last_raw_ratio;
    return LVDT_OK;
}

// Розрахунок лінеаризованого переміщення штока у міліметрах
lvdt_status_t lvdt_process_position(lvdt_handle_t *handle, float u_s1_amp, float u_s2_amp, float *position_mm) {
    if (handle == NULL || position_mm == NULL) {
        return LVDT_ERR_INVALID_PARAM;
    }

    float u_sum = u_s1_amp + u_s2_amp;
    if (u_sum < handle->config.min_sum_threshold) {
        handle->status_flags = LVDT_ERR_EXCITATION_LOST;
        return LVDT_ERR_EXCITATION_LOST;
    }

    float u_diff = u_s1_amp - u_s2_amp;
    float v_ratio = u_diff / u_sum;
    handle->last_raw_ratio = v_ratio;

    // Масштабування відносно нуля
    float x_raw = (v_ratio - handle->calibration.zero_offset_ratio) * handle->calibration.scale_factor_mm;

    // Обчислення полінома корекції: c0 + c1*x + c2*x^2 + c3*x^3
    float x_lin = handle->calibration.poly_c0 +
                  handle->calibration.poly_c1 * x_raw +
                  handle->calibration.poly_c2 * (x_raw * x_raw) +
                  handle->calibration.poly_c3 * (x_raw * x_raw * x_raw);

    handle->last_position_mm = x_lin;
    *position_mm = x_lin;
    handle->status_flags = LVDT_OK;
    return LVDT_OK;
}
