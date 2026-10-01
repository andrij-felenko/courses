// Вимірювання температури з комплексною діагностикою
pt100_status_t pt100_read_temperature_c(const pt100_config_t *config, float *out_temp_c) {
    if (out_temp_c == NULL) return PT100_ERR_INVALID_PARAM;

    uint32_t raw_adc = 0;
    if (afe_read_adc_raw(&raw_adc) != 0) {
        *out_temp_c = -999.0f;
        return PT100_ERR_COMMUNICATION;
    }

    // Аналіз обриву та короткого замикання
    if (raw_adc >= 0xFFFFFE) {
        *out_temp_c = -999.0f;
        return PT100_ERR_OPEN_CIRCUIT;
    }
    if (raw_adc <= 100) {
        *out_temp_c = -999.0f;
        return PT100_ERR_SHORT_CIRCUIT;
    }

    // Обчислення опору та лінеаризація
    float r_rtd = config->r_ref_ohms * ((float)raw_adc / 8388607.0f);
    if (r_rtd < 18.5f || r_rtd > 390.5f) {
        *out_temp_c = -999.0f;
        return PT100_ERR_OUT_OF_RANGE;
    }

    *out_temp_c = calculate_cvd_temperature(r_rtd, config->r_0_ohms);
    return PT100_OK;
}
