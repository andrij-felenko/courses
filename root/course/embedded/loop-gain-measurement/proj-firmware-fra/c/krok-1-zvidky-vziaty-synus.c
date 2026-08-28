#include <stdint.h>
#include <math.h>

#define LUT_BITS  10                 // 2^10 = 1024 точки на період
#define LUT_SIZE  (1u << LUT_BITS)
#define LUT_MASK  (LUT_SIZE - 1u)

static float sine_lut[LUT_SIZE];

void sine_lut_init(void) {
    for (uint32_t i = 0; i < LUT_SIZE; i++)
        sine_lut[i] = sinf(2.0f * (float)M_PI * i / LUT_SIZE);
}

// Фаза — ціле з фіксованою комою: старші LUT_BITS бітів індексують таблицю.
// phase += step щокроку; step задає частоту. Перенос розряду = «обгортка» періоду
// сама собою, без жодного if — у цьому вся краса фазового акумулятора.
static inline float sine_from_phase(uint32_t phase) {
    return sine_lut[(phase >> (32 - LUT_BITS)) & LUT_MASK];
}
static inline float cosine_from_phase(uint32_t phase) {
    return sine_lut[((phase >> (32 - LUT_BITS)) + LUT_SIZE / 4u) & LUT_MASK];
}
