rtd_status_t rtd_process_sample(rtd_ctx_t *ctx, float raw_r_meas, float *out_temperature) {
    if (!ctx || !out_temperature) {
        return RTD_ERR_INVALID_ARG;
    }

    // 1. Апаратна діагностика
    rtd_status_t diag_status = rtd_diagnose(ctx, raw_r_meas);
    if (diag_status != RTD_OK) {
        *out_temperature = -999.0f;
        return diag_status;
    }

    // 2. Двоточкове калібрування
    float r_cal = (raw_r_meas - ctx->zero_offset) * ctx->span_gain;

    // 3. Лінеаризація
    return rtd_calc_temperature(ctx, r_cal, out_temperature);
}

void rtd_processing_task(void *pvParameters) {
    rtd_ctx_t *rtd_ctx = (rtd_ctx_t *)pvParameters;
    float current_temp = 0.0f;

    while (1) {
        float raw_resistance = 108.57f; // Виміряний опір (~22 °C)

        rtd_status_t status = rtd_process_sample(rtd_ctx, raw_resistance, &current_temp);

        if (status == RTD_OK) {
            // Передача точної температури в регулятор
        } else {
            // Аварійна зупинка нагріву при помилці
        }
    }
}
