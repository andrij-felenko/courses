esp_err_t as5048_calibrate_zero(as5048_handle_t handle)
{
    if (!handle) {
        return ESP_ERR_INVALID_ARG;
    }

    uint16_t current_raw = 0;
    esp_err_t ret = as5048_read_raw_angle(handle, &current_raw);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося зчитати кут для калібрування нуля");
        return ret;
    }

    handle->zero_offset = current_raw;
    ESP_LOGI(TAG, "Встановлено новий zero_offset = %u (0x%04X)", current_raw, current_raw);
    return ESP_OK;
}
