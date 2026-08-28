#include <stdint.h>
#include <stdbool.h>

#define SQRT3       1.732050807568877f
#define SQRT3_HALF  0.8660254037844386f
#define ONE_AND_HALF 1.5f

typedef struct {
    float v_alpha;      // Вхідна напруга alpha [В]
    float v_beta;       // Вхідна напруга beta [В]
    float v_dc;         // Напруга шини DC [В]
    uint16_t arr;       // Період лічильника таймера
} SvpwmInput;

typedef struct {
    uint16_t ccr_a;     // Поріг таймера для фази A
    uint16_t ccr_b;     // Поріг таймера для фази B
    uint16_t ccr_c;     // Поріг таймера для фази C
    uint8_t sector;     // Номер сектора (1..6)
} SvpwmOutput;

static const uint8_t SECTOR_MAP[8] = { 0, 2, 6, 1, 4, 3, 5, 0 };

SvpwmOutput svpwm_calculate(const SvpwmInput* in) {
    SvpwmOutput out;
    if (in->v_dc <= 0.0f || in->arr == 0) {
        out.ccr_a = in->arr / 2;
        out.ccr_b = in->arr / 2;
        out.ccr_c = in->arr / 2;
        out.sector = 0;
        return out;
    }

    // 1. Швидка ідентифікація сектора
    float u1 = in->v_beta;
    float u2 = SQRT3_HALF * in->v_alpha - 0.5f * in->v_beta;
    float u3 = -SQRT3_HALF * in->v_alpha - 0.5f * in->v_beta;

    uint8_t code = 0;
    if (u1 > 0.0f) code |= 1;
    if (u2 > 0.0f) code |= 2;
    if (u3 > 0.0f) code |= 4;

    uint8_t sector = SECTOR_MAP[code];
    out.sector = sector;

    // 2. Базові проекції тривалостей
    float scale = (float)in->arr / in->v_dc;
    float x = SQRT3 * scale * in->v_beta;
    float y = scale * (ONE_AND_HALF * in->v_alpha + SQRT3_HALF * in->v_beta);
    float z = scale * (-ONE_AND_HALF * in->v_alpha + SQRT3_HALF * in->v_beta);

    // 3. Вибір активних інтервалів
    float t1 = 0.0f, t2 = 0.0f;
    switch (sector) {
        case 1: t1 = -z; t2 =  x; break;
        case 2: t1 =  z; t2 =  y; break;
        case 3: t1 =  x; t2 = -y; break;
        case 4: t1 = -x; t2 =  z; break;
        case 5: t1 = -y; t2 = -z; break;
        case 6: t1 =  y; t2 = -x; break;
        default: t1 = 0.0f; t2 = 0.0f; break;
    }

    // 4. Захист від перемодуляції
    float t_sum = t1 + t2;
    float arr_f = (float)in->arr;
    if (t_sum > arr_f) {
        float norm = arr_f / t_sum;
        t1 *= norm;
        t2 *= norm;
    }

    // 5. Симетричний 7-сегментний розподіл
    float t0 = arr_f - t1 - t2;
    float ta = t0 * 0.25f;
    float tb = ta + t1 * 0.5f;
    float tc = tb + t2 * 0.5f;

    // 6. Призначення фазам
    switch (sector) {
        case 1:
            out.ccr_a = (uint16_t)ta;
            out.ccr_b = (uint16_t)tb;
            out.ccr_c = (uint16_t)tc;
            break;
        case 2:
            out.ccr_a = (uint16_t)tb;
            out.ccr_b = (uint16_t)ta;
            out.ccr_c = (uint16_t)tc;
            break;
        case 3:
            out.ccr_a = (uint16_t)tc;
            out.ccr_b = (uint16_t)ta;
            out.ccr_c = (uint16_t)tb;
            break;
        case 4:
            out.ccr_a = (uint16_t)tc;
            out.ccr_b = (uint16_t)tb;
            out.ccr_c = (uint16_t)ta;
            break;
        case 5:
            out.ccr_a = (uint16_t)tb;
            out.ccr_b = (uint16_t)tc;
            out.ccr_c = (uint16_t)ta;
            break;
        case 6:
            out.ccr_a = (uint16_t)ta;
            out.ccr_b = (uint16_t)tc;
            out.ccr_c = (uint16_t)tb;
            break;
        default:
            out.ccr_a = in->arr / 2;
            out.ccr_b = in->arr / 2;
            out.ccr_c = in->arr / 2;
            break;
    }

    return out;
}
