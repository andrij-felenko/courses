#include <stdint.h>
#include <math.h>

// Стан одного детектора Ґерцеля.
typedef struct { float coeff, s1, s2; } goertzel_t;

static void g_reset(goertzel_t *g) { g->s1 = 0.0f; g->s2 = 0.0f; }

// Стала фільтра від номера біна k у вікні з N відліків.
static void g_set_bin(goertzel_t *g, int k, uint32_t N) {
    g->coeff = 2.0f * cosf(2.0f * (float)M_PI * k / (float)N);
    g_reset(g);
}

static inline void g_push(goertzel_t *g, float x) {
    float s = x + g->coeff * g->s1 - g->s2;
    g->s2 = g->s1;
    g->s1 = s;
}

// Дістати дійсну й уявну частини біна з кінцевого стану (потрібна фаза, не лише модуль).
static void g_result(const goertzel_t *g, int k, uint32_t N, float *re, float *im) {
    float w  = 2.0f * (float)M_PI * k / (float)N;
    float cw = cosf(w), sw = sinf(w);
    *re = g->s1 - g->s2 * cw;     // дійсна частина біна
    *im = g->s2 * sw;             // уявна частина біна
}
