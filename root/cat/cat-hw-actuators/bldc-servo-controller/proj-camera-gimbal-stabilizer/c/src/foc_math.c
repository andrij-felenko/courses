#include "foc_math.h"
#include <math.h>
#include <stddef.h>

/**
 * @file foc_math.c
 * @brief Реалізація перетворень Кларка, Парка та Space Vector Modulation (SVPWM).
 */

/**
 * @brief Нормалізація кута ротора в діапазон [0, 2*PI).
 */
float foc_normalize_angle(float angle_rad) {
    float two_pi = 2.0f * M_PI;
    while (angle_rad < 0.0f) {
        angle_rad += two_pi;
    }
    while (angle_rad >= two_pi) {
        angle_rad -= two_pi;
    }
    return angle_rad;
}

/**
 * @brief Обчислення синуса та косинуса.
 */
void foc_sincos(float angle_rad, float *sin_out, float *cos_out) {
    float norm_angle = foc_normalize_angle(angle_rad);
    if (sin_out != NULL) *sin_out = sinf(norm_angle);
    if (cos_out != NULL) *cos_out = cosf(norm_angle);
}

/**
 * @brief Пряме перетворення Кларка (I_a, I_b, I_c -> I_alpha, I_beta).
 * i_alpha = i_a
 * i_beta = (i_a + 2*i_b) / sqrt(3)
 */
void foc_clarke_transform(float i_a, float i_b, float i_c, foc_alphabeta_t *out_ab) {
    if (out_ab == NULL) return;

    (void)i_c; /* При симетричному навантаженні i_a + i_b + i_c = 0 */
    out_ab->alpha = i_a;
    out_ab->beta = ONE_BY_SQRT3 * (i_a + 2.0f * i_b);
}

/**
 * @brief Зворотне перетворення Кларка (V_alpha, V_beta -> V_a, V_b, V_c).
 */
void foc_inv_clarke_transform(const foc_alphabeta_t *in_ab, foc_abc_t *out_abc) {
    if (in_ab == NULL || out_abc == NULL) return;

    out_abc->a = in_ab->alpha;
    out_abc->b = -0.5f * in_ab->alpha + (SQRT3 * 0.5f) * in_ab->beta;
    out_abc->c = -0.5f * in_ab->alpha - (SQRT3 * 0.5f) * in_ab->beta;
}

/**
 * @brief Пряме перетворення Парка (I_alpha, I_beta -> I_d, I_q).
 * i_d = i_alpha * cos(theta) + i_beta * sin(theta)
 * i_q = -i_alpha * sin(theta) + i_beta * cos(theta)
 */
void foc_park_transform(const foc_alphabeta_t *in_ab, float theta_rad, foc_dq_t *out_dq) {
    if (in_ab == NULL || out_dq == NULL) return;

    float sin_t = 0.0f, cos_t = 0.0f;
    foc_sincos(theta_rad, &sin_t, &cos_t);

    out_dq->d =  in_ab->alpha * cos_t + in_ab->beta * sin_t;
    out_dq->q = -in_ab->alpha * sin_t + in_ab->beta * cos_t;
}

/**
 * @brief Зворотне перетворення Парка (V_d, V_q -> V_alpha, V_beta).
 * v_alpha = v_d * cos(theta) - v_q * sin(theta)
 * v_beta  = v_d * sin(theta) + v_q * cos(theta)
 */
void foc_inv_park_transform(const foc_dq_t *in_dq, float theta_rad, foc_alphabeta_t *out_ab) {
    if (in_dq == NULL || out_ab == NULL) return;

    float sin_t = 0.0f, cos_t = 0.0f;
    foc_sincos(theta_rad, &sin_t, &cos_t);

    out_ab->alpha = in_dq->d * cos_t - in_dq->q * sin_t;
    out_ab->beta  = in_dq->d * sin_t + in_dq->q * cos_t;
}

/**
 * @brief Векторна модуляція ШІМ (Space Vector PWM / SVPWM з інжекцією третьої гармоніки).
 * @param v_alpha Альфа-компонента напруги.
 * @param v_beta Бета-компонента напруги.
 * @param v_dc Напруга живильної шини постійного струму (V).
 * @param d_a [out] Вихідне заповнення фази A [0.0 ... 1.0].
 * @param d_b [out] Вихідне заповнення фази B [0.0 ... 1.0].
 * @param d_c [out] Вихідне заповнення фази C [0.0 ... 1.0].
 */
void foc_svpwm(float v_alpha, float v_beta, float v_dc, float *d_a, float *d_b, float *d_c) {
    if (d_a == NULL || d_b == NULL || d_c == NULL || v_dc <= 0.0f) return;

    /* 1. Нормалізація напруг відносно Vdc */
    foc_alphabeta_t v_ab = { .alpha = v_alpha / v_dc, .beta = v_beta / v_dc };

    /* 2. Зворотний Кларк для отримання опорних напруг фаз */
    foc_abc_t v_abc;
    foc_inv_clarke_transform(&v_ab, &v_abc);

    /* 3. Знаходження мінімуму та максимуму для інжекції нульової послідовності (Zero-Sequence Voltage) */
    float v_min = v_abc.a;
    if (v_abc.b < v_min) v_min = v_abc.b;
    if (v_abc.c < v_min) v_min = v_abc.c;

    float v_max = v_abc.a;
    if (v_abc.b > v_max) v_max = v_abc.b;
    if (v_abc.c > v_max) v_max = v_abc.c;

    /* Зсув нейтралі для максимального використання шини живлення на 15.5% */
    float v_zero = 0.5f * (v_min + v_max);

    /* 4. Розрахунок центрованого коефіцієнта заповнення (Mid-point PWM) */
    float duty_a = v_abc.a - v_zero + 0.5f;
    float duty_b = v_abc.b - v_zero + 0.5f;
    float duty_c = v_abc.c - v_zero + 0.5f;

    /* Обмеження діапазону [0.0, 1.0] */
    if (duty_a < 0.0f) duty_a = 0.0f; else if (duty_a > 1.0f) duty_a = 1.0f;
    if (duty_b < 0.0f) duty_b = 0.0f; else if (duty_b > 1.0f) duty_b = 1.0f;
    if (duty_c < 0.0f) duty_c = 0.0f; else if (duty_c > 1.0f) duty_c = 1.0f;

    *d_a = duty_a;
    *d_b = duty_b;
    *d_c = duty_c;
}
