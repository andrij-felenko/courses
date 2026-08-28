#include <stdint.h>
#include <math.h>

#define SR      48000u          // частота дискретизації, Гц
#define LUT_BITS 10
#define LUT_SIZE (1u << LUT_BITS)   // 1024 точки на період

static int16_t SINE[LUT_SIZE];

void sine_table_init(void) {
    for (uint32_t i = 0; i < LUT_SIZE; i++) {
        double a = 2.0 * M_PI * (double)i / (double)LUT_SIZE;
        SINE[i] = (int16_t)lround(32767.0 * sin(a));
    }
}

// Перетворення «частота → крок акумулятора фази» (32-бітна фаза)
static inline uint32_t phase_inc(double f_hz) {
    return (uint32_t)((f_hz / (double)SR) * 4294967296.0);   // 2^32
}

// Синус за 32-бітною фазою: старші LUT_BITS біт — індекс таблиці
static inline int16_t sine_at(uint32_t phase) {
    return SINE[phase >> (32 - LUT_BITS)];
}
