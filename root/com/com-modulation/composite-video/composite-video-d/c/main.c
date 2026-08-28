#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PAL_FS_HZ          17734475.0
#define PAL_SAMPLES_LINE   1135
#define PAL_FSC_HZ         4433618.75
#define PI_CONST           3.14159265358979323846

#define DAC_SYNC_LEVEL     0
#define DAC_BLANK_LEVEL    73
#define DAC_WHITE_LEVEL    255
#define DAC_BURST_AMPL     36

typedef struct {
    float y;
    float u;
    float v;
} EbuBar;

static const EbuBar BARS_75[8] = {
    { 0.75f,  0.000f,  0.000f }, /* Білий */
    { 0.64f, -0.327f,  0.075f }, /* Жовтий */
    { 0.53f,  0.110f, -0.461f }, /* Ціан */
    { 0.41f, -0.217f, -0.386f }, /* Зелений */
    { 0.34f,  0.217f,  0.386f }, /* Пурпур */
    { 0.23f, -0.110f,  0.461f }, /* Червоний */
    { 0.11f,  0.327f, -0.075f }, /* Синій */
    { 0.00f,  0.000f,  0.000f }  /* Чорний */
};

void synthesize_pal_line(uint8_t *out_samples, uint32_t line_num) {
    bool v_switch = (line_num % 2 != 0);
    double omega = 2.0 * PI_CONST * PAL_FSC_HZ / PAL_FS_HZ;
    double burst_phase = v_switch ? (3.0 * PI_CONST / 4.0) : (-3.0 * PI_CONST / 4.0);

    const uint32_t t_sync_start  = 27;  /* 1.5 мкс FP */
    const uint32_t t_sync_end    = 110; /* 4.7 мкс Sync */
    const uint32_t t_burst_start = 126; /* Breezeway */
    const uint32_t t_burst_end   = 170; /* 10 циклів Burst */
    const uint32_t t_active      = 213; /* Кінець BP (12.0 мкс) */

    for (uint32_t i = 0; i < PAL_SAMPLES_LINE; ++i) {
        if (i < t_sync_start) {
            out_samples[i] = DAC_BLANK_LEVEL;
        } else if (i < t_sync_end) {
            out_samples[i] = DAC_SYNC_LEVEL;
        } else if (i < t_burst_start) {
            out_samples[i] = DAC_BLANK_LEVEL;
        } else if (i < t_burst_end) {
            double b = DAC_BURST_AMPL * sin(omega * (double)i + burst_phase);
            int32_t val = (int32_t)(DAC_BLANK_LEVEL + b + 0.5);
            out_samples[i] = (uint8_t)(val < 0 ? 0 : (val > 255 ? 255 : val));
        } else if (i < t_active) {
            out_samples[i] = DAC_BLANK_LEVEL;
        } else {
            uint32_t active_idx = i - t_active;
            uint32_t bar_w = (PAL_SAMPLES_LINE - t_active) / 8;
            uint32_t idx = active_idx / bar_w;
            if (idx > 7) idx = 7;

            const EbuBar *b = &BARS_75[idx];
            double y_dac = DAC_BLANK_LEVEL + b->y * (DAC_WHITE_LEVEL - DAC_BLANK_LEVEL);

            double v_sign = v_switch ? -1.0 : 1.0;
            double u_sub = b->u * sin(omega * (double)i);
            double v_sub = v_sign * b->v * cos(omega * (double)i);
            double c_dac = (u_sub + v_sub) * (DAC_WHITE_LEVEL - DAC_BLANK_LEVEL);

            int32_t total = (int32_t)(y_dac + c_dac + 0.5);
            out_samples[i] = (uint8_t)(total < 0 ? 0 : (total > 255 ? 255 : total));
        }
    }
}
