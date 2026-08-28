/*
 * line_diagnostics.c - Реалізація математики моніторингу та класифікації станів
 */

#include "line_diagnostics.h"
#include <math.h>
#include <string.h>

void line_diag_init(line_diag_handle_t *handle, const line_diag_config_t *config)
{
    if (!handle || !config) {
        return;
    }
    handle->config = *config;
    handle->sample_idx = 0;
    handle->surge_counter = 0;
    handle->current_state = LINE_STATE_OK;
    memset(handle->adc_buffer, 0, sizeof(handle->adc_buffer));
}

void line_diag_push_adc_sample(line_diag_handle_t *handle, uint16_t adc_raw)
{
    if (!handle) {
        return;
    }
    handle->adc_buffer[handle->sample_idx] = adc_raw;
    handle->sample_idx = (handle->sample_idx + 1U) % LINE_DIAG_SAMPLE_WINDOW_SIZE;
}

static float adc_to_vcm(const line_diag_config_t *cfg, uint16_t raw)
{
    float v_adc = ((float)raw * cfg->adc_vref_volts) / 4095.0f;
    float v_centered = v_adc - (cfg->adc_vref_volts * 0.5f);
    return v_centered * cfg->divider_ratio;
}

void line_diag_process(line_diag_handle_t *handle, float raw_r_iso_adc, line_health_metrics_t *out_metrics)
{
    if (!handle || !out_metrics) {
        return;
    }

    float sum_v = 0.0f;
    float sum_sq_diff = 0.0f;
    const uint32_t n = LINE_DIAG_SAMPLE_WINDOW_SIZE;

    for (uint32_t i = 0; i < n; ++i) {
        float v = adc_to_vcm(&handle->config, handle->adc_buffer[i]);
        sum_v += v;
    }
    float mean_v = sum_v / (float)n;

    for (uint32_t i = 0; i < n; ++i) {
        float v = adc_to_vcm(&handle->config, handle->adc_buffer[i]);
        float diff = v - mean_v;
        sum_sq_diff += diff * diff;
    }
    float rms_noise = sqrtf(sum_sq_diff / (float)n);

    uint32_t last_idx = (handle->sample_idx + LINE_DIAG_SAMPLE_WINDOW_SIZE - 1U) % LINE_DIAG_SAMPLE_WINDOW_SIZE;
    out_metrics->v_cm_instant_volts = adc_to_vcm(&handle->config, handle->adc_buffer[last_idx]);
    out_metrics->v_cm_dc_bias_volts = mean_v;
    out_metrics->v_cm_noise_rms_volts = rms_noise;
    out_metrics->surge_event_count = handle->surge_counter;

    /* Розрахунок опору ізоляції за напругою на шунті R_shunt = 10 кОм */
    if (raw_r_iso_adc <= 0.01f) {
        out_metrics->insulation_res_kohm = 10000.0f;
    } else {
        const float r_shunt = 10.0f; /* кОм */
        const float v_test = 24.0f;  /* В */
        float i_leak_ma = raw_r_iso_adc / r_shunt;
        out_metrics->insulation_res_kohm = (i_leak_ma > 0.0001f) ? ((v_test - raw_r_iso_adc) / i_leak_ma) : 10000.0f;
    }

    /* Автомат рішень безпеки */
    if (out_metrics->insulation_res_kohm < handle->config.r_iso_min_kohm) {
        out_metrics->state = LINE_STATE_CRITICAL_INSULATION_FAIL;
    } else if (out_metrics->v_cm_noise_rms_volts > handle->config.v_cm_rms_warn_threshold_volts) {
        out_metrics->state = LINE_STATE_WARNING_NO_GROUND;
    } else if (fabsf(out_metrics->v_cm_dc_bias_volts) > handle->config.v_cm_warn_threshold_volts) {
        out_metrics->state = LINE_STATE_WARNING_HIGH_COMMON_MODE;
    } else {
        out_metrics->state = LINE_STATE_OK;
    }

    handle->current_state = out_metrics->state;
}
