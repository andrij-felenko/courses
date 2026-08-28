#include <stdint.h>

#define Q15_ONE          32768
#define Q15_SQRT3        56756   // 1.7320508 * 32768
#define Q15_SQRT3_HALF   28378   // 0.8660254 * 32768
#define Q15_ONE_AND_HALF 49152   // 1.5 * 32768

typedef struct {
    int16_t q_alpha;    // Q15 напруга V_alpha / V_dc [-32768..32767]
    int16_t q_beta;     // Q15 напруга V_beta / V_dc  [-32768..32767]
    uint16_t arr;       // Період таймера
} SvpwmQ15Input;

typedef struct {
    uint16_t ccr_a;
    uint16_t ccr_b;
    uint16_t ccr_c;
    uint8_t sector;
} SvpwmQ15Output;

static const uint8_t SECTOR_MAP_Q15[8] = { 0, 2, 6, 1, 4, 3, 5, 0 };

SvpwmQ15Output svpwm_q15_calc(const SvpwmQ15Input* in) {
    SvpwmQ15Output out;

    // 1. Ідентифікація сектора
    int32_t u1 = in->q_beta;
    int32_t u2 = ((int32_t)Q15_SQRT3_HALF * in->q_alpha - (int32_t)(Q15_ONE / 2) * in->q_beta) >> 15;
    int32_t u3 = (-(int32_t)Q15_SQRT3_HALF * in->q_alpha - (int32_t)(Q15_ONE / 2) * in->q_beta) >> 15;

    uint8_t code = 0;
    if (u1 > 0) code |= 1;
    if (u2 > 0) code |= 2;
    if (u3 > 0) code |= 4;

    uint8_t sector = SECTOR_MAP_Q15[code];
    out.sector = sector;

    // 2. Базові складові в масштабі ARR
    int32_t x = (((int32_t)Q15_SQRT3 * in->q_beta) >> 15) * in->arr >> 15;
    int32_t y = (((int32_t)Q15_ONE_AND_HALF * in->q_alpha + (int32_t)Q15_SQRT3_HALF * in->q_beta) >> 15) * in->arr >> 15;
    int32_t z = (((int32_t)-Q15_ONE_AND_HALF * in->q_alpha + (int32_t)Q15_SQRT3_HALF * in->q_beta) >> 15) * in->arr >> 15;

    // 3. Активні часи
    int32_t t1 = 0, t2 = 0;
    switch (sector) {
        case 1: t1 = -z; t2 =  x; break;
        case 2: t1 =  z; t2 =  y; break;
        case 3: t1 =  x; t2 = -y; break;
        case 4: t1 = -x; t2 =  z; break;
        case 5: t1 = -y; t2 = -z; break;
        case 6: t1 =  y; t2 = -x; break;
        default: break;
    }

    // 4. Обмеження перемодуляції
    int32_t t_sum = t1 + t2;
    if (t_sum > in->arr && t_sum > 0) {
        t1 = (t1 * in->arr) / t_sum;
        t2 = (t2 * in->arr) / t_sum;
    }

    // 5. Симетричні пороги
    int32_t t0 = in->arr - t1 - t2;
    uint16_t ta = (uint16_t)(t0 >> 2);
    uint16_t tb = (uint16_t)(ta + (t1 >> 1));
    uint16_t tc = (uint16_t)(tb + (t2 >> 1));

    switch (sector) {
        case 1: out.ccr_a = ta; out.ccr_b = tb; out.ccr_c = tc; break;
        case 2: out.ccr_a = tb; out.ccr_b = ta; out.ccr_c = tc; break;
        case 3: out.ccr_a = tc; out.ccr_b = ta; out.ccr_c = tb; break;
        case 4: out.ccr_a = tc; out.ccr_b = tb; out.ccr_c = ta; break;
        case 5: out.ccr_a = tb; out.ccr_b = tc; out.ccr_c = ta; break;
        case 6: out.ccr_a = ta; out.ccr_b = tc; out.ccr_c = tb; break;
        default:
            out.ccr_a = in->arr >> 1;
            out.ccr_b = in->arr >> 1;
            out.ccr_c = in->arr >> 1;
            break;
    }

    return out;
}
