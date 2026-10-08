#include <math.h>
#include <stdint.h>
#include <stdbool.h>

// Структура цифрового фільтра другого порядку (Biquad HPF) для відсікання інфразвуку
typedef struct {
    float b0, b1, b2, a1, a2;
    float x1, x2, y1, y2;
} biquad_hpf_t;

// Ініціалізація ФВЧ Баттерворта для захисту 5 Вт / 8 Ом динаміка від перевантаження
void biquad_hpf_init(biquad_hpf_t *f, float cutoff_hz, float sample_rate) {
    float w0 = 2.0f * 3.14159265f * cutoff_hz / sample_rate;
    float cos_w0 = cosf(w0);
    float alpha = sinf(w0) / (2.0f * 0.7071f); // Q = 0.7071 (Butterworth)

    float a0 = 1.0f + alpha;
    f->b0 = ((1.0f + cos_w0) / 2.0f) / a0;
    f->b1 = (-(1.0f + cos_w0)) / a0;
    f->b2 = ((1.0f + cos_w0) / 2.0f) / a0;
    f->a1 = (-2.0f * cos_w0) / a0;
    f->a2 = (1.0f - alpha) / a0;

    f->x1 = f->x2 = f->y1 = f->y2 = 0.0f;
}

// Обробка аудіовідліку: фільтрація ФВЧ та програмне лімітування амплітуди від кліпінгу
int16_t process_speaker_sample(biquad_hpf_t *f, int16_t in_sample, int16_t max_limit) {
    float x = (float)in_sample;
    float y = f->b0 * x + f->b1 * f->x1 + f->b2 * f->x2 - f->a1 * f->y1 - f->a2 * f->y2;

    f->x2 = f->x1;
    f->x1 = x;
    f->y2 = f->y1;
    f->y1 = y;

    // Жорсткий піковий лімітер для запобігання тепловому перегріву та кліпінгу BTL
    if (y > max_limit) y = (float)max_limit;
    if (y < -max_limit) y = -(float)max_limit;

    return (int16_t)y;
}
