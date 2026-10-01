#include <math.h>
#include <stdint.h>

typedef struct {
    float sensitivity;
    uint16_t zero_adc;
    uint16_t adc_max;
    float vref;
} acs712_config_t;

float acs712_read_dc(uint16_t adc_raw, const acs712_config_t *cfg) {
    int32_t diff = (int32_t)adc_raw - (int32_t)cfg->zero_adc;
    float voltage_diff = ((float)diff * cfg->vref) / (float)cfg->adc_max;
    return voltage_diff / cfg->sensitivity;
}

float acs712_read_rms(const uint16_t *samples, uint16_t count, const acs712_config_t *cfg) {
    float sum_sq = 0.0f;
    for (uint16_t i = 0; i < count; i++) {
        float current = acs712_read_dc(samples[i], cfg);
        sum_sq += current * current;
    }
    return sqrtf(sum_sq / (float)count);
}
