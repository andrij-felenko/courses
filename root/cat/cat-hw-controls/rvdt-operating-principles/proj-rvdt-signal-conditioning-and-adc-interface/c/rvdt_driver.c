#include "rvdt_driver.h"

void rvdt_init(const rvdt_config_t *cfg, rvdt_data_t *data) {
    if (!data) return;
    data->v1_filtered = 0.0f;
    data->v2_filtered = 0.0f;
    data->ratiometric_value = 0.0f;
    data->angle_degrees = 0.0f;
    data->status = RVDT_STATUS_OK;
}

rvdt_status_t rvdt_process_samples(const rvdt_config_t *cfg, rvdt_data_t *data, float raw_v1, float raw_v2) {
    if (!cfg || !data) return RVDT_STATUS_EXC_FAULT;

    float alpha = cfg->lpf_alpha;
    data->v1_filtered = alpha * raw_v1 + (1.0f - alpha) * data->v1_filtered;
    data->v2_filtered = alpha * raw_v2 + (1.0f - alpha) * data->v2_filtered;

    float sum_v = data->v1_filtered + data->v2_filtered;

    if (sum_v < cfg->min_sum_voltage) {
        data->status = RVDT_STATUS_OPEN_CIRCUIT;
        return data->status;
    }
    if (sum_v > cfg->max_sum_voltage) {
        data->status = RVDT_STATUS_SHORT_CIRCUIT;
        return data->status;
    }

    float diff_v = data->v1_filtered - data->v2_filtered;
    data->ratiometric_value = diff_v / sum_v;

    float norm_ratio = data->ratiometric_value - cfg->zero_offset_ratio;
    data->angle_degrees = norm_ratio * cfg->sensitivity_deg_per_ratio;

    data->status = RVDT_STATUS_OK;
    return data->status;
}
