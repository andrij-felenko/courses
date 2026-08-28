#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_MICS 4
#define FRAME_LEN 512
#define SOUND_SPEED 343.0f
#define MIC_STEP 0.042f // крок 4.2 см

// Розрахунок різниці затримок між сусідніми мікрофонами для кута theta_deg
static float compute_tdoa_seconds(float theta_deg, float spacing, float c) {
    float rad = theta_deg * (3.14159265f / 180.0f);
    return spacing * sinf(rad) / c;
}

// Застосування фазування Delay-and-Sum над багатоканальним кадровим буфером
void apply_delay_and_sum(const float in[NUM_MICS][FRAME_LEN], float* out,
                         int len, float fs, float steer_deg) {
    float rad = steer_deg * (3.14159265f / 180.0f);

    for (int i = 0; i < len; i++) {
        out[i] = 0.0f;
    }

    for (int m = 0; m < NUM_MICS; m++) {
        float delay_sec = (float)m * MIC_STEP * sinf(rad) / SOUND_SPEED;
        float shift_samples = delay_sec * fs;
        int s_int = (int)floorf(shift_samples);
        float s_frac = shift_samples - (float)s_int;

        for (int i = 0; i < len; i++) {
            int idx = i + s_int;
            float sample = 0.0f;
            if (idx >= 0 && idx + 1 < len) {
                sample = (1.0f - s_frac) * in[m][idx] + s_frac * in[m][idx + 1];
            } else if (idx >= 0 && idx < len) {
                sample = in[m][idx];
            }
            out[i] += sample / (float)NUM_MICS;
        }
    }
}
