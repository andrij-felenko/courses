#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    float q0, q1, q2, q3;    /* Одиничний кватерніон орієнтації */
    float integralFBx;       /* Інтегратор похибки осі X (компенсація bias) */
    float integralFBy;       /* Інтегратор похибки осі Y */
    float integralFBz;       /* Інтегратор похибки осі Z */
    float twoKp;             /* Подвоєний пропорційний коефіцієнт (2 * Kp) */
    float twoKi;             /* Подвоєний інтегральний коефіцієнт (2 * Ki) */
} MahonyFilter_t;

static inline float inv_sqrtf(float x) {
    return 1.0f / sqrtf(x);
}

void mahony_init(MahonyFilter_t *filter, float kp, float ki) {
    filter->q0 = 1.0f;
    filter->q1 = 0.0f;
    filter->q2 = 0.0f;
    filter->q3 = 0.0f;
    filter->integralFBx = 0.0f;
    filter->integralFBy = 0.0f;
    filter->integralFBz = 0.0f;
    filter->twoKp = 2.0f * kp;
    filter->twoKi = 2.0f * ki;
}

void mahony_update_6dof(MahonyFilter_t *filter,
                        float gx, float gy, float gz,
                        float ax, float ay, float az,
                        float dt) {
    float recipNorm;
    float halfvx, halfvy, halfvz;
    float halfex, halfey, halfez;
    float qa, qb, qc;

    /* 1. Перевірка валідності вектора акселерометра */
    float a_norm_sq = ax * ax + ay * ay + az * az;
    if (a_norm_sq > 0.0001f) {
        /* Нормалізація вимірів акселерометра */
        recipNorm = inv_sqrtf(a_norm_sq);
        ax *= recipNorm;
        ay *= recipNorm;
        az *= recipNorm;

        /* Динамічний гейтинг прискорень: перевірка діапазону 0.8g .. 1.2g */
        float a_mag = 1.0f / recipNorm;
        if (a_mag > 0.80f && a_mag < 1.20f) {
            /* Очікуваний напрямок гравітації у зв'язаній системі координат */
            halfvx = filter->q1 * filter->q3 - filter->q0 * filter->q2;
            halfvy = filter->q0 * filter->q1 + filter->q2 * filter->q3;
            halfvz = filter->q0 * filter->q0 - 0.5f + filter->q3 * filter->q3;

            /* Векторний добуток виміряного та очікуваного векторів гравітації */
            halfex = (ay * halfvz - az * halfvy);
            halfey = (az * halfvx - ax * halfvz);
            halfez = (ax * halfvy - ay * halfvx);

            /* Інтегральна складова корекції гіроскопа (bias tracking) */
            if (filter->twoKi > 0.0f) {
                filter->integralFBx += filter->twoKi * halfex * dt;
                filter->integralFBy += filter->twoKi * halfey * dt;
                filter->integralFBz += filter->twoKi * halfez * dt;
                gx += filter->integralFBx;
                gy += filter->integralFBy;
                gz += filter->integralFBz;
            }

            /* Пропорційна складова корекції */
            gx += filter->twoKp * halfex;
            gy += filter->twoKp * halfey;
            gz += filter->twoKp * halfez;
        }
    }

    /* 2. Інтегрування рівняння кінематики кватерніона */
    gx *= (0.5f * dt);
    gy *= (0.5f * dt);
    gz *= (0.5f * dt);
    qa = filter->q0;
    qb = filter->q1;
    qc = filter->q2;

    filter->q0 += (-qb * gx - qc * gy - filter->q3 * gz);
    filter->q1 += ( qa * gx + qc * gz - filter->q3 * gy);
    filter->q2 += ( qa * gy - qb * gz + filter->q3 * gx);
    filter->q3 += ( qa * gz + qb * gy - qc * gx);

    /* 3. Унітарна нормалізація кватерніона */
    recipNorm = inv_sqrtf(filter->q0 * filter->q0 +
                          filter->q1 * filter->q1 +
                          filter->q2 * filter->q2 +
                          filter->q3 * filter->q3);
    filter->q0 *= recipNorm;
    filter->q1 *= recipNorm;
    filter->q2 *= recipNorm;
    filter->q3 *= recipNorm;
}

void mahony_get_euler(const MahonyFilter_t *filter, float *roll, float *pitch, float *yaw) {
    float q0 = filter->q0, q1 = filter->q1, q2 = filter->q2, q3 = filter->q3;
    *roll  = atan2f(2.0f * (q0 * q1 + q2 * q3), 1.0f - 2.0f * (q1 * q1 + q2 * q2));
    *pitch = asinf(2.0f * (q0 * q2 - q3 * q1));
    *yaw   = atan2f(2.0f * (q0 * q3 + q1 * q2), 1.0f - 2.0f * (q2 * q2 + q3 * q3));
}
