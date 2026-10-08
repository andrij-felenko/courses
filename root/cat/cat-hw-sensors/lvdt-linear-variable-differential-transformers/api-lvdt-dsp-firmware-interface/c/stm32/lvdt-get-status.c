// Отримання поточної бітової маски несправностей LVDT
lvdt_status_t lvdt_get_status(const lvdt_handle_t *handle, uint32_t *fault_mask) {
    if (handle == NULL || fault_mask == NULL) {
        return LVDT_ERR_INVALID_PARAM;
    }

    *fault_mask = 0;

    // Перевірка прапорців стану
    if (handle->status_flags == LVDT_ERR_EXCITATION_LOST) {
        *fault_mask |= (1U << 0); // Втрата збудження
    }
    if (handle->last_raw_ratio > handle->config.max_ratio_limit || 
        handle->last_raw_ratio < -handle->config.max_ratio_limit) {
        *fault_mask |= (1U << 1); // Вихід за межі лінійного ратіо
    }

    return handle->status_flags;
}
