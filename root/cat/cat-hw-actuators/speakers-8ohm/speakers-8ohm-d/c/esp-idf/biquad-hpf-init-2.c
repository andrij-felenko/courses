#include <math.h>
#include <stdint.h>
#include <stdbool.h>

// Структура коефіцієнтів та стану цифрового біквадратного фільтра (Biquad HPF)
typedef struct {
    float b0, b1, b2;
    float a1, a2;
    float x1, x2;
    float y1, y2;
} biquad_hpf_t;

// Ініціалізація коефіцієнтів ФВЧ Баттерворта 2-го порядку
void biquad_hpf_init(biquad_hpf_t *f, float sample_rate, float cutoff_freq) {
    float w0 = 2.0f * M_PI * cutoff_freq / sample_rate;
    float cos_w0 = cosf(w0);
    float alpha = sinf(w0) / (2.0f * 0.7071f); // Q = 0.7071 (Баттерворт)

    float a0 = 1.0f + alpha;
    f->b0 = ((1.0f + cos_w0) / 2.0f) / a0;
    f->b1 = (-(1.0f + cos_w0)) / a0;
    f->b2 = ((1.0f + cos_w0) / 2.0f) / a0;
    f->a1 = (-2.0f * cos_w0) / a0;
    f->a2 = (1.0f - alpha) / a0;

    f->x1 = f->x2 = 0.0f;
    f->y1 = f->y2 = 0.0f;
}

// Обробка одного відліку аудіосигналу біквадратним фільтром
float biquad_hpf_process(biquad_hpf_t *f, float in) {
    float out = f->b0 * in + f->b1 * f->x1 + f->b2 * f->x2 - f->a1 * f->y1 - f->a2 * f->y2;
    f->x2 = f->x1;
    f->x1 = in;
    f->y2 = f->y1;
    f->y1 = out;
    return out;
}

// Функція цифрового лімітування амплітуди для захисту 5 Вт динаміка
float speaker_limit_sample(float sample, float max_amplitude) {
    if (sample > max_amplitude) {
        return max_amplitude;
    } else if (sample < -max_amplitude) {
        return -max_amplitude;
    }
    return sample;
}

// Обробка блоку відліків аудіосигналу (DSP-конвеєр)
void process_audio_buffer(float *buffer, size_t num_samples, biquad_hpf_t *hpf, float max_peak) {
    for (size_t i = 0; i < num_samples; i++) {
        float filtered = biquad_hpf_process(hpf, buffer[i]);
        buffer[i] = speaker_limit_sample(filtered, max_peak);
    }
}
