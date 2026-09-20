// Повна діагностика вимірювального тракту RVDT
rvdt_status_t rvdt_diagnose_and_read(rvdt_handle_t *handle, uint16_t raw_v1, uint16_t raw_v2, float *angle_deg) {
    if (!handle || !angle_deg) {
        return RVDT_STATUS_ERR_PARAM;
    }

    float v1 = (float)raw_v1;
    float v2 = (float)raw_v2;
    float sum = v1 + v2;

    // 1. Детекція обриву або втрати збудження
    if (sum < (float)(handle->config.adc_max_raw * 0.05f)) {
        return RVDT_STATUS_ERR_OPEN_WINDING;
    }

    // 2. Зчитування кута
    rvdt_status_t status = rvdt_read_angle(handle, raw_v1, raw_v2, angle_deg);
    if (status != RVDT_STATUS_OK) {
        return status;
    }

    // 3. Перевірка на вихід за межі лінійного діапазону (наприклад, ±60 градусів)
    if (*angle_deg > 60.0f || *angle_deg < -60.0f) {
        return RVDT_STATUS_ERR_OUT_OF_RANGE;
    }

    return RVDT_STATUS_OK;
}
