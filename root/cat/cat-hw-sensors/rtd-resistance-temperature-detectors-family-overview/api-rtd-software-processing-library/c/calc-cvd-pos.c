static float calc_cvd_pos(float r_t, float r0, float a, float b) {
    float poly_term = 1.0f - (r_t / r0);
    float discriminant = (a * a) - (4.0f * b * poly_term);
    if (discriminant < 0.0f) {
        return -999.0f; // Помилка дискримінанта
    }
    return (-a + sqrtf(discriminant)) / (2.0f * b);
}

typedef struct {
    float r;
    float t;
} rtd_lut_entry_t;

static const rtd_lut_entry_t rtd_lut[] = {
    { 80.31f, -50.0f},
    {100.00f,   0.0f},
    {119.40f,  50.0f},
    {138.51f, 100.0f},
    {157.33f, 150.0f}
};
static const size_t rtd_lut_size = sizeof(rtd_lut) / sizeof(rtd_lut[0]);

static float calc_lut(float r_t) {
    if (r_t <= rtd_lut[0].r) return rtd_lut[0].t;
    if (r_t >= rtd_lut[rtd_lut_size - 1].r) return rtd_lut[rtd_lut_size - 1].t;

    for (size_t i = 0; i < rtd_lut_size - 1; i++) {
        if (r_t >= rtd_lut[i].r && r_t <= rtd_lut[i+1].r) {
            float r_diff = rtd_lut[i+1].r - rtd_lut[i].r;
            float t_diff = rtd_lut[i+1].t - rtd_lut[i].t;
            return rtd_lut[i].t + ((r_t - rtd_lut[i].r) * t_diff / r_diff);
        }
    }
    return 0.0f;
}

rtd_status_t rtd_calc_temperature(const rtd_ctx_t *ctx, float r_cal, float *temp_out) {
    if (!ctx || !ctx->initialized || !temp_out) {
        return RTD_ERR_INVALID_ARG;
    }

    if (ctx->config.mode == RTD_CALC_CVD) {
        *temp_out = calc_cvd_pos(r_cal, ctx->config.r0, ctx->config.cvd_a, ctx->config.cvd_b);
    } else {
        *temp_out = calc_lut(r_cal);
    }

    return RTD_OK;
}
