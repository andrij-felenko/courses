// Біквадратна ланка (IIR 2-го порядку), форма DF2T.
// Зберігає 2 числа стану між викликами — справжній потоковий фільтр.
typedef struct {
    float b0, b1, b2;   // коефіцієнти чисельника
    float a1, a2;       // коефіцієнти знаменника (a0 нормований до 1)
    float z1, z2;       // стан (дві затримки)
} biquad_t;

static inline float biquad_step(biquad_t *f, float x) {
    float y = f->b0 * x + f->z1;
    f->z1   = f->b1 * x - f->a1 * y + f->z2;
    f->z2   = f->b2 * x - f->a2 * y;
    return y;
}
