// Реалізація фільтра, яку перевіряємо — тут БІХ-біквад (Direct Form I).
// Стан — два попередні входи й виходи; коефіцієнти з проєктування.
typedef struct {
    float b0, b1, b2, a1, a2;     // коефіцієнти (a0 нормований до 1)
    float x1, x2, y1, y2;         // пам'ять
} Biquad;

static float biquad_step(Biquad *q, float x) {
    float y = q->b0*x + q->b1*q->x1 + q->b2*q->x2
                      - q->a1*q->y1 - q->a2*q->y2;
    q->x2 = q->x1; q->x1 = x;
    q->y2 = q->y1; q->y1 = y;
    return y;
}

// Зміряти |H| на одній частоті: подати синус, дати усталитися, зняти амплітуду.
// (M_PI не гарантований під strict-C на МК, тож задаємо число явно.)
#define TWO_PI 6.283185307179586f
static float biquad_mag_at(Biquad proto, float f, float fs_sample) {
    Biquad q = proto;                          // свіжа копія зі станом = 0
    const float w = TWO_PI * f / fs_sample;
    float peak = 0.0f;
    const int settle = 2000, measure = 4000;   // спершу усталення, тоді вимір
    for (int n = 0; n < settle + measure; ++n) {
        float x = sinf(w * (float)n);
        float y = biquad_step(&q, x);
        if (n >= settle) {
            float a = fabsf(y);
            if (a > peak) peak = a;            // амплітуда входу = 1, тож peak = |H|
        }
    }
    return peak;                               // |H(f)| у разах
}

// Промір характеристики на логарифмічній сітці частот.
// ВАЖЛИВО: сітку згущуємо біля країв смуг — там маска найтісніша (див. пастки).
static void sweep(Biquad proto, const FilterSpec *s,
                  const float *freq, float *mag_out, size_t n) {
    for (size_t i = 0; i < n; ++i)
        mag_out[i] = biquad_mag_at(proto, freq[i], s->fs_sample);
}
