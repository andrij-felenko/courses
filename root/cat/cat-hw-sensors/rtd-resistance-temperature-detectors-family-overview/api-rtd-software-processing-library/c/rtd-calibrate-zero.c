rtd_status_t rtd_calibrate_zero(rtd_ctx_t *ctx, float r_meas1, float r_ref1) {
    if (!ctx || !ctx->initialized || r_meas1 <= 0.0f || r_ref1 <= 0.0f) {
        return RTD_ERR_INVALID_ARG;
    }
    ctx->zero_offset = r_meas1 - (r_ref1 / ctx->span_gain);
    return RTD_OK;
}

rtd_status_t rtd_calibrate_span(rtd_ctx_t *ctx, float r_meas1, float r_ref1, float r_meas2, float r_ref2) {
    if (!ctx || !ctx->initialized) {
        return RTD_ERR_INVALID_ARG;
    }
    float delta_meas = r_meas2 - r_meas1;
    float delta_ref  = r_ref2 - r_ref1;

    if (fabsf(delta_meas) < 1e-6f || fabsf(delta_ref) < 1e-6f) {
        return RTD_ERR_INVALID_ARG;
    }

    ctx->span_gain = delta_ref / delta_meas;
    ctx->zero_offset = r_meas1 - (r_ref1 / ctx->span_gain);
    return RTD_OK;
}
