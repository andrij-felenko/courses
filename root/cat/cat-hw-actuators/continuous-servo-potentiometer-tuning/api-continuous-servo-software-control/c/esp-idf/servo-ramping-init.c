#include <stdint.h>
#include <math.h>

typedef struct {
    float current_pulse_us;
    float target_pulse_us;
    float max_step_us;
} servo_ramping_t;

void servo_ramping_init(servo_ramping_t* ramp, float init_pulse, float ramp_sec, float dt_sec) {
    ramp->current_pulse_us = init_pulse;
    ramp->target_pulse_us = init_pulse;
    float total_steps = ramp_sec / dt_sec;
    ramp->max_step_us = 500.0f / total_steps;
}

uint32_t servo_ramping_step(servo_ramping_t* ramp) {
    float diff = ramp->target_pulse_us - ramp->current_pulse_us;
    if (fabsf(diff) <= ramp->max_step_us) {
        ramp->current_pulse_us = ramp->target_pulse_us;
    } else {
        ramp->current_pulse_us += (diff > 0.0f) ? ramp->max_step_us : -ramp->max_step_us;
    }
    return (uint32_t)lroundf(ramp->current_pulse_us);
}
