// Калібрування електричного нуля за поточним положенням
rvdt_status_t rvdt_calibrate_zero(rvdt_handle_t *handle, uint16_t raw_v1, uint16_t raw_v2) {
    float current_angle = 0.0f;
    handle->zero_offset_deg = 0.0f; // тимчасове скидання для заміру
    rvdt_status_t status = rvdt_read_angle(handle, raw_v1, raw_v2, &current_angle);
    if (status == RVDT_STATUS_OK) {
        handle->zero_offset_deg = current_angle;
    }
    return status;
}

// Експоненційне згладжування відфільтрованого кута
float rvdt_filter_angle(float previous_filtered, float new_measured, float alpha) {
    return previous_filtered + alpha * (new_measured - previous_filtered);
}
