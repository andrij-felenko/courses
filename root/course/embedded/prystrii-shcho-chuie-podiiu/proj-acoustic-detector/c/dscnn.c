#include "dscnn.h"

#include <stdint.h>

/* Ваги й параметри переквантування — вивантаження з навчання, model_weights.c. */
extern const int8_t  DSCNN_L1_W[36];   /* conv 3×3, 1 канал → 4, [oc][ky][kx] */
extern const int32_t DSCNN_L1_B[4];
extern const dscnn_requant_t DSCNN_L1_RQ;

extern const int8_t  DSCNN_L2_W[36];   /* depthwise 3×3 на 4 канали, [c][ky][kx] */
extern const int32_t DSCNN_L2_B[4];
extern const dscnn_requant_t DSCNN_L2_RQ;

extern const int8_t  DSCNN_L3_W[32];   /* pointwise 4→8, [oc][ic] */
extern const int32_t DSCNN_L3_B[8];
extern const dscnn_requant_t DSCNN_L3_RQ;

extern const int8_t  DSCNN_L4_W[72];   /* depthwise 3×3 на 8 каналів */
extern const int32_t DSCNN_L4_B[8];
extern const dscnn_requant_t DSCNN_L4_RQ;

extern const int8_t  DSCNN_L5_W[64];   /* pointwise 8→8 */
extern const int32_t DSCNN_L5_B[8];
extern const dscnn_requant_t DSCNN_L5_RQ;

extern const int8_t  DSCNN_FC_W[32];   /* повнозв'язний 8→4, [oc][i] */
extern const int32_t DSCNN_FC_B[4];
extern const float   DSCNN_OUTPUT_SCALE;

/* Розміри карт ознак по шарах. */
#define L1_H 20
#define L1_W 16
#define L1_C 4
#define L2_H 10
#define L2_W 8
#define L2_C 4
#define L3_C 8

/* Дві робочі карти. Більша (1280 байтів) тримає вихід першої згортки,
 * менша (640) — усе, що після другого кроку по часу й частоті. Шари
 * перекидають дані з однієї в іншу, тож третьої не треба. */
static int8_t buf_a[L1_H * L1_W * L1_C];
static int8_t buf_b[L2_H * L2_W * L3_C];

/* Множення з насиченням і округленням, старша половина результату (Q31).
 * Це те саме, що робить SMMULR на Cortex-M, і те саме, що робить
 * gemmlowp у tflite-micro — переносити модель на інший рушій можна,
 * не переучуючи її. */
static int32_t sat_round_doubling_high_mul(int32_t a, int32_t b)
{
    if (a == INT32_MIN && b == INT32_MIN) {
        return INT32_MAX;
    }

    const int64_t product = (int64_t)a * (int64_t)b;
    const int64_t nudge = (product >= 0) ? (1 << 30) : (1 - (1 << 30));

    return (int32_t)((product + nudge) / ((int64_t)1 << 31));
}

/* Правий зсув з округленням до найближчого (половини — від нуля). */
static int32_t rounding_shift_right(int32_t x, uint8_t shift)
{
    if (shift == 0) {
        return x;
    }

    const int32_t mask = ((int32_t)1 << shift) - 1;
    const int32_t remainder = x & mask;
    const int32_t threshold = (mask >> 1) + ((x < 0) ? 1 : 0);

    return (x >> shift) + ((remainder > threshold) ? 1 : 0);
}

/* Акумулятор int32 → активація int8 із ReLU.
 * Нульова точка активацій нульова (симетричне квантування), тому ReLU —
 * це просто нижня межа 0, а доповнення нулями на краях згортки не вносить
 * зсуву: нуль у квантованій шкалі означає рівно нуль. */
static int8_t requantize_relu(int32_t acc, dscnn_requant_t rq)
{
    int32_t v = rounding_shift_right(sat_round_doubling_high_mul(acc, rq.multiplier), rq.shift);

    if (v < 0) {
        v = 0;
    } else if (v > 127) {
        v = 127;
    }

    return (int8_t)v;
}

/* Перший шар: звичайна згортка 3×3 з кроком 2 по обох осях, один вхідний
 * канал (матриця ознак), доповнення нулями по краях. */
static void conv3x3_stride2_mono(const int8_t features[AED_NUM_FRAMES][AED_MEL_BINS],
                                 int8_t *out)
{
    for (int oy = 0; oy < L1_H; ++oy) {
        for (int ox = 0; ox < L1_W; ++ox) {
            for (int oc = 0; oc < L1_C; ++oc) {
                int32_t acc = DSCNN_L1_B[oc];

                for (int ky = 0; ky < 3; ++ky) {
                    const int iy = oy * 2 - 1 + ky;
                    if (iy < 0 || iy >= AED_NUM_FRAMES) {
                        continue;
                    }
                    for (int kx = 0; kx < 3; ++kx) {
                        const int ix = ox * 2 - 1 + kx;
                        if (ix < 0 || ix >= AED_MEL_BINS) {
                            continue;
                        }
                        acc += (int32_t)DSCNN_L1_W[oc * 9 + ky * 3 + kx] *
                               (int32_t)features[iy][ix];
                    }
                }

                out[(oy * L1_W + ox) * L1_C + oc] = requantize_relu(acc, DSCNN_L1_RQ);
            }
        }
    }
}

/* Глибинна згортка 3×3: кожен канал згортається своїм ядром і ні з ким
 * не змішується. Розкладка карти — NHWC, тобто канали лежать поруч. */
static void depthwise3x3(const int8_t *in, int h, int w, int ch, int stride,
                         const int8_t *wts, const int32_t *bias,
                         dscnn_requant_t rq, int8_t *out)
{
    const int oh = (h + stride - 1) / stride;
    const int ow = (w + stride - 1) / stride;

    for (int oy = 0; oy < oh; ++oy) {
        for (int ox = 0; ox < ow; ++ox) {
            for (int c = 0; c < ch; ++c) {
                int32_t acc = bias[c];

                for (int ky = 0; ky < 3; ++ky) {
                    const int iy = oy * stride - 1 + ky;
                    if (iy < 0 || iy >= h) {
                        continue;
                    }
                    for (int kx = 0; kx < 3; ++kx) {
                        const int ix = ox * stride - 1 + kx;
                        if (ix < 0 || ix >= w) {
                            continue;
                        }
                        acc += (int32_t)wts[c * 9 + ky * 3 + kx] *
                               (int32_t)in[(iy * w + ix) * ch + c];
                    }
                }

                out[(oy * ow + ox) * ch + c] = requantize_relu(acc, rq);
            }
        }
    }
}

/* Точкова згортка 1×1: у кожній точці карти — маленьке матричне множення,
 * яке й перемішує канали між собою. */
static void pointwise(const int8_t *in, int points, int in_ch, int out_ch,
                      const int8_t *wts, const int32_t *bias,
                      dscnn_requant_t rq, int8_t *out)
{
    for (int p = 0; p < points; ++p) {
        for (int oc = 0; oc < out_ch; ++oc) {
            int32_t acc = bias[oc];

            for (int ic = 0; ic < in_ch; ++ic) {
                acc += (int32_t)wts[oc * in_ch + ic] * (int32_t)in[p * in_ch + ic];
            }

            out[p * out_ch + oc] = requantize_relu(acc, rq);
        }
    }
}

/* Усереднення по всій карті: 80 точок стискаються в один вектор із 8 чисел.
 * Саме тут мережа перестає залежати від того, у якій частині 640-мілісекундного
 * вікна стався звук. */
static void global_average_pool(const int8_t *in, int points, int ch, int8_t *out)
{
    for (int c = 0; c < ch; ++c) {
        int32_t sum = 0;
        for (int p = 0; p < points; ++p) {
            sum += in[p * ch + c];
        }
        out[c] = (int8_t)((sum + points / 2) / points);
    }
}

void dscnn_run(const int8_t features[AED_NUM_FRAMES][AED_MEL_BINS],
               float logits[AED_NUM_CLASSES])
{
    conv3x3_stride2_mono(features, buf_a);

    depthwise3x3(buf_a, L1_H, L1_W, L1_C, 2, DSCNN_L2_W, DSCNN_L2_B, DSCNN_L2_RQ, buf_b);
    pointwise(buf_b, L2_H * L2_W, L2_C, L3_C, DSCNN_L3_W, DSCNN_L3_B, DSCNN_L3_RQ, buf_a);

    depthwise3x3(buf_a, L2_H, L2_W, L3_C, 1, DSCNN_L4_W, DSCNN_L4_B, DSCNN_L4_RQ, buf_b);
    pointwise(buf_b, L2_H * L2_W, L3_C, L3_C, DSCNN_L5_W, DSCNN_L5_B, DSCNN_L5_RQ, buf_a);

    int8_t pooled[L3_C];
    global_average_pool(buf_a, L2_H * L2_W, L3_C, pooled);

    /* Останній шар лишається в int32: розквантовуємо один раз, уже логіти. */
    for (int oc = 0; oc < AED_NUM_CLASSES; ++oc) {
        int32_t acc = DSCNN_FC_B[oc];
        for (int i = 0; i < L3_C; ++i) {
            acc += (int32_t)DSCNN_FC_W[oc * L3_C + i] * (int32_t)pooled[i];
        }
        logits[oc] = (float)acc * DSCNN_OUTPUT_SCALE;
    }
}
