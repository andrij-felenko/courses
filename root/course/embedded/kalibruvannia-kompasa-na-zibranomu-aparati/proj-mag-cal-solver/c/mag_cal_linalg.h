/* ==========================================================================
 *  mag_cal_linalg.h — векторна й матрична алгебра конвеєра: усе на float,
 *  без динамічної пам'яті, без залежностей крім <math.h>.
 * ========================================================================== */
#ifndef MAG_CAL_LINALG_H
#define MAG_CAL_LINALG_H

#include <math.h>

#include "mag_cal_types.h"

static inline vec3_t vec3_add(vec3_t a, vec3_t b) {
    return (vec3_t){ a.x + b.x, a.y + b.y, a.z + b.z };
}

static inline vec3_t vec3_sub(vec3_t a, vec3_t b) {
    return (vec3_t){ a.x - b.x, a.y - b.y, a.z - b.z };
}

static inline vec3_t vec3_scale(vec3_t a, float k) {
    return (vec3_t){ a.x * k, a.y * k, a.z * k };
}

static inline float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline float vec3_norm(vec3_t a) {
    return sqrtf(vec3_dot(a, a));
}

static inline vec3_t mat3_mul_vec(const mat3_t *m, vec3_t v) {
    return (vec3_t){
        m->m[0][0] * v.x + m->m[0][1] * v.y + m->m[0][2] * v.z,
        m->m[1][0] * v.x + m->m[1][1] * v.y + m->m[1][2] * v.z,
        m->m[2][0] * v.x + m->m[2][1] * v.y + m->m[2][2] * v.z
    };
}

/* Одиничний вектор; для виродженого входу повертає надір {0,0,1} */
vec3_t vec3_unit(vec3_t a);

float mat3_det(const mat3_t *m);

/* Власні числа симетричної 3×3 у спадному порядку (замкнена формула Сміта) */
void mat3_sym_eigenvalues(const mat3_t *m, float out[3]);

/* Число зумовленості симетричної матриці: |λmax| / |λmin|.
 * Вироджена матриця дає велике скінченне число, а не нескінченність. */
float mat3_condition(const mat3_t *m);

/* Розв'язання щільної системи 9×9 методом Гаусса з частковим вибором
 * головного елемента. Матриця a руйнується. false — система вироджена. */
bool mag_cal_solve9(float a[9][9], const float b[9], float x[9]);

#endif /* MAG_CAL_LINALG_H */
