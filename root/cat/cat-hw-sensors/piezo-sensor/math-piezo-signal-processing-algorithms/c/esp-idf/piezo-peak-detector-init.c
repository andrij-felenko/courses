#include <math.h>
#include <stdint.h>

typedef struct {
    float state;
    float alpha;
    uint16_t zero_offset;
} piezo_peak_detector_t;

void piezo_peak_detector_init(piezo_peak_detector_t *detector, float alpha, uint16_t zero_offset) {
    detector->state = 0.0f;
    detector->alpha = alpha;
    detector->zero_offset = zero_offset;
}

float piezo_peak_detector_update(piezo_peak_detector_t *detector, uint16_t raw_adc) {
    float input_val = fabsf((float)raw_adc - (float)detector->zero_offset);
    float decayed_val = detector->state * detector->alpha;
    
    if (input_val > decayed_val) {
        detector->state = input_val;
    } else {
        detector->state = decayed_val;
    }
    
    return detector->state;
}
