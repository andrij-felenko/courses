rtd_status_t rtd_diagnose(const rtd_ctx_t *ctx, float r_meas) {
    if (!ctx || !ctx->initialized) {
        return RTD_ERR_INVALID_ARG;
    }

    uint8_t status = RTD_OK;

    if (r_meas >= ctx->config.r_max) {
        status |= RTD_ERR_OPEN_CIRCUIT;
    }
    if (r_meas <= ctx->config.r_min) {
        status |= RTD_ERR_SHORT_CIRCUIT;
    }

    return (rtd_status_t)status;
}
