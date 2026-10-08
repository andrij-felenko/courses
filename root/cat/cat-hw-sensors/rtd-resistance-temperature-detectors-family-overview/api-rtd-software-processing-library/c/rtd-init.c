#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    RTD_CALC_CVD = 0,
    RTD_CALC_LUT = 1
} rtd_calc_mode_t;

typedef struct {
    float r0;              // Номінальний опір при 0 °C (Ом)
    float alpha;           // Температурний коефіцієнт (1/°C)
    float cvd_a;           // Коефіцієнт CVD A
    float cvd_b;           // Коефіцієнт CVD B
    float cvd_c;           // Коефіцієнт CVD C
    float r_ref;           // Еталонний опір R_ref (Ом)
    float r_min;           // Мінімальний припустимий опір (Ом)
    float r_max;           // Максимальний припустимий опір (Ом)
    rtd_calc_mode_t mode;  // Режим обчислення (CVD або LUT)
} rtd_config_t;

typedef struct {
    rtd_config_t config;
    float zero_offset;     // Калібрувальний зсув нуля (Ом)
    float span_gain;       // Калібрувальний коефіцієнт підсилення
    bool initialized;
} rtd_ctx_t;

typedef enum {
    RTD_OK               = 0x00,
    RTD_ERR_OPEN_CIRCUIT = 0x01,
    RTD_ERR_SHORT_CIRCUIT= 0x02,
    RTD_ERR_OUT_OF_RANGE = 0x04,
    RTD_ERR_INVALID_ARG  = 0x08
} rtd_status_t;

rtd_status_t rtd_init(rtd_ctx_t *ctx, const rtd_config_t *cfg) {
    if (!ctx || !cfg) {
        return RTD_ERR_INVALID_ARG;
    }
    if (cfg->r0 <= 0.0f || cfg->r_ref <= 0.0f || cfg->r_min >= cfg->r_max) {
        return RTD_ERR_INVALID_ARG;
    }

    ctx->config = *cfg;
    ctx->zero_offset = 0.0f;
    ctx->span_gain = 1.0f;
    ctx->initialized = true;

    return RTD_OK;
}
