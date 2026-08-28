#include <stdint.h>
#include <stddef.h>

typedef struct {
    float vcc;          // В
    float sensitivity;  // В/мТл
    uint16_t adc_max;   // Код АЦП
    float v_quiescent;  // Напруга спокою В
} HallSensor_C;

void hall_init(HallSensor_C *sensor, float vcc, float sensitivity, uint16_t adc_max) {
    sensor->vcc = vcc;
    sensor->sensitivity = sensitivity;
    sensor->adc_max = adc_max;
    sensor->v_quiescent = vcc * 0.5f;
}

void hall_calibrate_zero(HallSensor_C *sensor, const uint16_t *adc_samples, size_t count) {
    if (count == 0 || adc_samples == NULL) return;
    float sum_v = 0.0f;
    for (size_t i = 0; i < count; ++i) {
        sum_v += ((float)adc_samples[i] / (float)sensor->adc_max) * sensor->vcc;
    }
    sensor->v_quiescent = sum_v / (float)count;
}

float hall_read_mT(const HallSensor_C *sensor, uint16_t adc_raw) {
    float v_out = ((float)adc_raw / (float)sensor->adc_max) * sensor->vcc;
    return (v_out - sensor->v_quiescent) / sensor->sensitivity;
}
