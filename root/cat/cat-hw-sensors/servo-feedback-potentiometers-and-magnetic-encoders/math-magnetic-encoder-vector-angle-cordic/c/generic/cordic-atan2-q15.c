#include <stdint.h>

static const uint16_t CORDIC_LUT16[14] = {
    8192, 4836, 2555, 1297, 651, 326, 163,
    81, 41, 20, 10, 5, 3, 1
};

uint16_t cordic_atan2_q15(int16_t x, int16_t y) {
    int32_t x_curr = x;
    int32_t y_curr = y;
    int32_t z_accum = 0;

    if (x_curr < 0) {
        if (y_curr >= 0) {
            int32_t temp = x_curr;
            x_curr = y_curr;
            y_curr = -temp;
            z_accum = 16384;
        } else {
            int32_t temp = x_curr;
            x_curr = -y_curr;
            y_curr = temp;
            z_accum = -16384;
        }
    }

    for (int i = 0; i < 14; i++) {
        int32_t x_next;
        int32_t y_next;
        uint16_t gamma = CORDIC_LUT16[i];

        if (y_curr > 0) {
            x_next = x_curr + (y_curr >> i);
            y_next = y_curr - (x_curr >> i);
            z_accum += gamma;
        } else {
            x_next = x_curr - (y_curr >> i);
            y_next = y_curr + (x_curr >> i);
            z_accum -= gamma;
        }

        x_curr = x_next;
        y_curr = y_next;
    }

    return (uint16_t)(z_accum & 0xFFFF);
}

typedef struct {
    int16_t offset_cos;
    int16_t offset_sin;
    int16_t a11, a12, a22;
    int32_t filt_cos;
    int32_t filt_sin;
    uint16_t prev_angle;
    int32_t total_turns;
} encoder_pipeline_t;

int32_t encoder_pipeline_step(encoder_pipeline_t *pipe, uint16_t raw_cos, uint16_t raw_sin) {
    pipe->filt_cos += ((int32_t)raw_cos - (pipe->filt_cos >> 4));
    pipe->filt_sin += ((int32_t)raw_sin - (pipe->filt_sin >> 4));

    int16_t u_cos = (int16_t)(pipe->filt_cos >> 4) - pipe->offset_cos;
    int16_t u_sin = (int16_t)(pipe->filt_sin >> 4) - pipe->offset_sin;

    int16_t v_cos = (int16_t)(((int32_t)pipe->a11 * u_cos + (int32_t)pipe->a12 * u_sin) >> 12);
    int16_t v_sin = (int16_t)(((int32_t)pipe->a22 * u_sin) >> 12);

    uint16_t curr_angle = cordic_atan2_q15(v_cos, v_sin);

    int16_t diff = (int16_t)(curr_angle - pipe->prev_angle);
    pipe->total_turns += diff;
    pipe->prev_angle = curr_angle;

    return pipe->total_turns;
}
