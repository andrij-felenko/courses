typedef struct { float coeff, s1, s2; int n, N; } goertzel_t;

void g_init(goertzel_t *g, int N, float target, float fs) {
    int k = (int)(0.5f + (float)N * target / fs);
    g->coeff = 2.0f * cosf(2.0f * (float)M_PI * k / N);
    g->s1 = g->s2 = 0.0f;
    g->n = 0;
    g->N = N;
}

// викликати на кожен новий відлік; повертає 1, коли набрано N (power готовий)
int g_push(goertzel_t *g, float x, float *power) {
    float s = x + g->coeff * g->s1 - g->s2;
    g->s2 = g->s1;
    g->s1 = s;
    if (++g->n < g->N) return 0;
    *power = g->s1 * g->s1 + g->s2 * g->s2 - g->coeff * g->s1 * g->s2;
    g->s1 = g->s2 = 0.0f;  // скидаємо на наступний блок
    g->n  = 0;
    return 1;
}
