#ifndef FOC_MATH_H
#define FOC_MATH_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file foc_math.h
 * @brief Оголошення математичних типів даних та векторних перетворень Кларка/Парка.
 */

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

#define SQRT3            1.7320508075688772f
#define ONE_BY_SQRT3     0.5773502691896258f
#define TWO_BY_SQRT3     1.1547005383792515f

/**
 * @brief Величини у 3-фазній стаціонарній системі координат (A, B, C).
 */
typedef struct {
    float a;
    float b;
    float c;
} foc_abc_t;

/**
 * @brief Величини у 2-фазній ортогональній стаціонарній системі координат (Alpha, Beta).
 */
typedef struct {
    float alpha;
    float beta;
} foc_alphabeta_t;

/**
 * @brief Величини у 2-фазній обертовій роторній системі координат (d, q).
 */
typedef struct {
    float d;
    float q;
} foc_dq_t;

/* Прототипи функцій векторного керування */
void foc_clarke_transform(float i_a, float i_b, float i_c, foc_alphabeta_t *out_ab);
void foc_inv_clarke_transform(const foc_alphabeta_t *in_ab, foc_abc_t *out_abc);
void foc_park_transform(const foc_alphabeta_t *in_ab, float theta_rad, foc_dq_t *out_dq);
void foc_inv_park_transform(const foc_dq_t *in_dq, float theta_rad, foc_alphabeta_t *out_ab);
void foc_sincos(float angle_rad, float *sin_out, float *cos_out);
float foc_normalize_angle(float angle_rad);
void foc_svpwm(float v_alpha, float v_beta, float v_dc, float *d_a, float *d_b, float *d_c);

#endif /* FOC_MATH_H */
