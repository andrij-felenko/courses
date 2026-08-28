// Гарячий шлях модема: поправку беремо з таблиці, без exp/log.
// Точність log-MAP за ціну, близьку до голого max.
static float CORR[65];                 // ln(1+e^−x) для x ∈ [0,8), крок 1/8

void maxstar_init(void) {
    for (int i = 0; i < 65; i++)
        CORR[i] = logf(1.0f + expf(-i / 8.0f));
}

static inline float maxstar(float a, float b) {
    float d = a - b;
    float m = (d > 0.0f) ? a : b;
    float x = (d > 0.0f) ? d : -d;     // |a − b|
    if (x >= 8.0f) return m;           // поправка вже ≈ 0
    return m + CORR[(int)(x * 8.0f)];  // один доступ до таблиці
}
