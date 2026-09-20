// Обчислення кута на основі сирих відліків АЦП двох вторинних обмоток
rvdt_status_t rvdt_read_angle(rvdt_handle_t *handle, uint16_t raw_v1, uint16_t raw_v2, float *angle_deg) {
    if (!handle || !angle_deg || !handle->is_initialized) {
        return RVDT_STATUS_ERR_PARAM;
    }
    
    float v1 = (float)raw_v1;
    float v2 = (float)raw_v2;
    float sum = v1 + v2;
    
    // Перевірка на відсутність сигналу або обрив
    if (sum < 10.0f) {
        return RVDT_STATUS_ERR_OPEN_WINDING;
    }
    
    // Логометричне співвідношення
    float ratiometric = (v1 - v2) / sum;
    
    // Розрахунок кута в градусах з урахуванням чутливості та калібрування
    float raw_angle = (ratiometric / handle->config.sensitivity_v_v_deg) * handle->scale_factor;
    *angle_deg = raw_angle - handle->zero_offset_deg;
    
    return RVDT_STATUS_OK;
}
