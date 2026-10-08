#include <math.h>

typedef struct {
    float current_val;
    float target_val;
    float max_accel; // Максимальне прискорення (од/с)
} ramp_filter_t;

float ramp_filter_update(ramp_filter_t *ramp, float dt) {
    float max_change = ramp->max_accel * dt;
    float diff = ramp->target_val - ramp->current_val;

    if (diff > max_change) {
        ramp->current_val += max_change;
    } else if (diff < -max_change) {
        ramp->current_val -= max_change;
    } else {
        ramp->current_val = ramp->target_val;
    }

    return ramp->current_val;
}
