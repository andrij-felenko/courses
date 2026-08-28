#include <math.h>

typedef struct {
    float b0, b1, b2, a1, a2;   /* коефіцієнти, a0 зведено до 1 */
    float s1, s2;               /* стан: Direct Form II транспонована */
} Biquad;

/* Порахувати коефіцієнти режектора ОДИН раз при старті (RBJ notch). */
void notch_init(Biquad *bq, float f0, float fs, float Q)
{
    const float PI = 3.14159265f;                 /* не покладаймося на M_PI */
    float w0    = 2.0f * PI * f0 / fs;
    float cw    = cosf(w0);
    float alpha = sinf(w0) / (2.0f * Q);
    float a0    = 1.0f + alpha;
    bq->b0 =  1.0f          / a0;
    bq->b1 = -2.0f * cw     / a0;
    bq->b2 =  1.0f          / a0;
    bq->a1 = -2.0f * cw     / a0;
    bq->a2 = (1.0f - alpha) / a0;
    bq->s1 = bq->s2 = 0.0f;
}

/* Гарячий шлях: один семпл гіроскопа → відфільтрований. 8000 викликів/с на вісь. */
static inline float notch_apply(Biquad *bq, float x)
{
    float y = bq->b0 * x + bq->s1;
    bq->s1  = bq->b1 * x - bq->a1 * y + bq->s2;
    bq->s2  = bq->b2 * x - bq->a2 * y;
    return y;
}

/* --- використання --- */
Biquad notch_roll;                                /* по одному на кожну вісь */
/* при ініціалізації: */
notch_init(&notch_roll, 63.7f, 8000.0f, 6.0f);
/* у перерві готовності гіроскопа, 8000 разів на секунду: */
float gyro_clean = notch_apply(&notch_roll, gyro_raw);
