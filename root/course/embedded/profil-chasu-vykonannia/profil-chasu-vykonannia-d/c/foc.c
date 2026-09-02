#include "foc.h"

#include <math.h>

#define SIN_BITS   8U
#define SIN_SIZE   (1U << SIN_BITS)          /* 256 точок + дублікат нуля */
#define TWO_PI     6.28318530717958647692f
#define INV_SQRT3  0.57735026918962576451f
#define SQRT3_2    0.86602540378443864676f
#define DUTY_MIN   0.02f                     /* запас на мертвий час і заряд бутстрапа */
#define DUTY_MAX   0.98f

/* Глобальні дані лежать у SRAM — 0 тактів очікування на кожне читання. */
static float s_sin[SIN_SIZE + 1U];
static pi_t  s_pi_d;
static pi_t  s_pi_q;
static float s_id_ref;
static float s_iq_ref;

void foc_init(void)
{
    for (uint32_t i = 0U; i <= SIN_SIZE; ++i) {
        s_sin[i] = sinf(TWO_PI * (float)i / (float)SIN_SIZE);
    }

    s_pi_d.kp = 2.5f;
    s_pi_d.ki = 0.08f;
    s_pi_d.out_max = 12.0f;   /* вольти */
    s_pi_q = s_pi_d;
    foc_reset();
}

void foc_reset(void)
{
    s_pi_d.integ = 0.0f;
    s_pi_q.integ = 0.0f;
    s_id_ref = 0.0f;
    s_iq_ref = 0.0f;
}

void foc_set_targets(float id_ref, float iq_ref)
{
    s_id_ref = id_ref;
    s_iq_ref = iq_ref;
}

/* Лінійна інтерполяція по таблиці. Індекс і дріб дістаються зсувами:
   ні ділення, ні перевірок меж — межа знята дублікатом s_sin[SIN_SIZE]. */
static inline void sincos_q32(uint32_t phase, float *sn, float *cs)
{
    const uint32_t idx  = phase >> (32U - SIN_BITS);
    const uint32_t frac = (phase >> (32U - SIN_BITS - 16U)) & 0xFFFFU;
    const float    f    = (float)frac * (1.0f / 65536.0f);
    const uint32_t cdx  = (idx + (SIN_SIZE / 4U)) & (SIN_SIZE - 1U);   /* зсув на 90 градусів */

    *sn = s_sin[idx] + (s_sin[idx + 1U] - s_sin[idx]) * f;
    *cs = s_sin[cdx] + (s_sin[cdx + 1U] - s_sin[cdx]) * f;
}

/* Порівняння з константою компілюються у VCMP + IT — це умовне виконання,
   а не перехід, тож обидві гілки коштують однаково. */
static inline float clampf(float v, float lo, float hi)
{
    if (v < lo) {
        v = lo;
    }
    if (v > hi) {
        v = hi;
    }
    return v;
}

static inline float pi_step(pi_t *r, float err)
{
    r->integ += r->ki * err;
    /* Антивіндап: інтегратор затиснуто тією самою межею, що й вихід. */
    r->integ = clampf(r->integ, -r->out_max, r->out_max);
    return clampf(r->kp * err + r->integ, -r->out_max, r->out_max);
}

duty3_t foc_step(float ia, float ib, uint32_t theta_q32, float vdc)
{
    /* Пряме перетворення Кларка: третя фаза не вимірюється, ic = -(ia + ib). */
    const float i_alpha = ia;
    const float i_beta  = (ia + 2.0f * ib) * INV_SQRT3;

    float sn;
    float cs;
    sincos_q32(theta_q32, &sn, &cs);

    /* Пряме перетворення Парка: струми в системі ротора. */
    const float id =  i_alpha * cs + i_beta * sn;
    const float iq = -i_alpha * sn + i_beta * cs;

    float vd = pi_step(&s_pi_d, s_id_ref - id);
    float vq = pi_step(&s_pi_q, s_iq_ref - iq);

    /* Кругове обмеження вектора напруги: довжина не більша за vdc/sqrt(3).
       sqrtf тут це одна інструкція VSQRT.F32 (14 тактів) за умови складання
       з -fno-math-errno — інакше GCC додасть перевірку й виклик у libm. */
    const float v_max = vdc * INV_SQRT3;
    const float v_sq  = vd * vd + vq * vq;
    if (v_sq > v_max * v_max) {
        const float scale = v_max / sqrtf(v_sq);
        vd *= scale;
        vq *= scale;
        s_pi_d.integ *= scale;   /* інтегратор не копить те, що не вийшло на міст */
        s_pi_q.integ *= scale;
    }

    /* Зворотний Парк і зворотний Кларк. */
    const float v_alpha = vd * cs - vq * sn;
    const float v_beta  = vd * sn + vq * cs;

    const float va = v_alpha;
    const float vb = -0.5f * v_alpha + SQRT3_2 * v_beta;
    const float vc = -0.5f * v_alpha - SQRT3_2 * v_beta;

    /* Інжекція середньої точки — той самий результат, що й SVPWM,
       але без пошуку сектора: жодного розгалуження за даними. */
    float hi = va;
    float lo = va;
    if (vb > hi) { hi = vb; }
    if (vc > hi) { hi = vc; }
    if (vb < lo) { lo = vb; }
    if (vc < lo) { lo = vc; }
    const float mid = 0.5f * (hi + lo);
    const float k   = 1.0f / vdc;

    duty3_t d;
    d.a = clampf(0.5f + (va - mid) * k, DUTY_MIN, DUTY_MAX);
    d.b = clampf(0.5f + (vb - mid) * k, DUTY_MIN, DUTY_MAX);
    d.c = clampf(0.5f + (vc - mid) * k, DUTY_MIN, DUTY_MAX);
    return d;
}
