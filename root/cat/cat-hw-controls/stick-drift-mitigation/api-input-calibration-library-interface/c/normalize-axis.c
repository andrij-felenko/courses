#include <math.h>

static float normalize_axis(uint16_t raw, const input_axis_config_t *cfg) {
    if (raw >= cfg->adc_center) {
        uint16_t span = cfg->adc_max - cfg->adc_center;
        return (span > 0) ? (float)(raw - cfg->adc_center) / (float)span : 0.0f;
    } else {
        uint16_t span = cfg->adc_center - cfg->adc_min;
        return (span > 0) ? -(float)(cfg->adc_center - raw) / (float)span : 0.0f;
    }
}

input_error_t input_update(uint16_t raw_x, uint16_t raw_y,
                             const input_profile_t *profile,
                             input_vector_t *out_vec) {
    if (profile == NULL || out_vec == NULL) {
        return INPUT_ERR_INVALID_PARAM;
    }

    float norm_x = normalize_axis(raw_x, &profile->axis_x);
    float norm_y = normalize_axis(raw_y, &profile->axis_y);

    if (profile->use_radial_deadzone) {
        float magnitude = sqrtf(norm_x * norm_x + norm_y * norm_y);
        float dz_in = profile->axis_x.deadzone_inner;
        float dz_out = profile->axis_x.deadzone_outer;

        if (magnitude <= dz_in) {
            norm_x = 0.0f;
            norm_y = 0.0f;
        } else if (magnitude >= dz_out) {
            float scale = 1.0f / magnitude;
            norm_x *= scale;
            norm_y *= scale;
        } else {
            float scale = (magnitude - dz_in) / (dz_out - dz_in) / magnitude;
            norm_x *= scale;
            norm_y *= scale;
        }
    }

    out_vec->x = norm_x;
    out_vec->y = norm_y;
    return INPUT_OK;
}
