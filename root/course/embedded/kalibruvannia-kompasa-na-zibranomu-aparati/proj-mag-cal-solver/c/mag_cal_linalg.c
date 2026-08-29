/* ==========================================================================
 *  mag_cal_linalg.c — реалізація алгебри: власні числа симетричної 3×3
 *  та прямий розв'язувач 9×9 з вибором головного елемента.
 * ========================================================================== */

#include "mag_cal_linalg.h"

vec3_t vec3_unit(vec3_t a) {
    const float n = vec3_norm(a);
    if (!(n > 1e-6f)) {                 /* заразом ловить NaN */
        return (vec3_t){ 0.0f, 0.0f, 1.0f };
    }
    return vec3_scale(a, 1.0f / n);
}

float mat3_det(const mat3_t *m) {
    return m->m[0][0] * (m->m[1][1] * m->m[2][2] - m->m[1][2] * m->m[2][1])
         - m->m[0][1] * (m->m[1][0] * m->m[2][2] - m->m[1][2] * m->m[2][0])
         + m->m[0][2] * (m->m[1][0] * m->m[2][1] - m->m[1][1] * m->m[2][0]);
}

/* Замкнена формула для власних чисел симетричної 3×3 (O. Smith, 1961).
 * Ітеративний QR тут зайвий: матриця мала, а формула детермінована за часом. */
void mat3_sym_eigenvalues(const mat3_t *m, float out[3]) {
    const float a01 = m->m[0][1], a02 = m->m[0][2], a12 = m->m[1][2];
    const float p1 = a01 * a01 + a02 * a02 + a12 * a12;

    if (p1 < 1e-12f) {                  /* матриця вже діагональна */
        float d[3] = { m->m[0][0], m->m[1][1], m->m[2][2] };
        for (int i = 0; i < 2; i++) {   /* сортування трьох чисел спаданням */
            for (int j = i + 1; j < 3; j++) {
                if (d[j] > d[i]) { const float t = d[i]; d[i] = d[j]; d[j] = t; }
            }
        }
        out[0] = d[0]; out[1] = d[1]; out[2] = d[2];
        return;
    }

    const float q = (m->m[0][0] + m->m[1][1] + m->m[2][2]) / 3.0f;
    const float e0 = m->m[0][0] - q, e1 = m->m[1][1] - q, e2 = m->m[2][2] - q;
    const float p2 = e0 * e0 + e1 * e1 + e2 * e2 + 2.0f * p1;
    const float p  = sqrtf(p2 / 6.0f);

    /* B = (A - qI) / p; det(B)/2 лежить у [-1, +1] з точністю до округлення */
    mat3_t b;
    const float inv_p = 1.0f / p;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            b.m[i][j] = inv_p * (m->m[i][j] - (i == j ? q : 0.0f));
        }
    }

    float r = mat3_det(&b) * 0.5f;
    if (r < -1.0f) r = -1.0f;
    if (r >  1.0f) r =  1.0f;

    const float phi = acosf(r) / 3.0f;
    const float eig_max = q + 2.0f * p * cosf(phi);
    const float eig_min = q + 2.0f * p * cosf(phi + 2.0943951f);   /* + 2π/3 */

    out[0] = eig_max;
    out[2] = eig_min;
    out[1] = 3.0f * q - eig_max - eig_min;                          /* слід сталий */
}

float mat3_condition(const mat3_t *m) {
    /* NaN у матриці дав би NaN і тут, а NaN >= порогу — це false, тобто
     * вироджене калібрування мовчки пройшло б гейт зумовленості. */
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (!isfinite(m->m[i][j])) {
                return 1.0e6f;
            }
        }
    }

    float eig[3];
    mat3_sym_eigenvalues(m, eig);

    float max_abs = fabsf(eig[0]);
    float min_abs = fabsf(eig[0]);
    for (int i = 1; i < 3; i++) {
        const float a = fabsf(eig[i]);
        if (a > max_abs) max_abs = a;
        if (a < min_abs) min_abs = a;
    }

    if (min_abs < 1e-6f) {
        return 1.0e6f;      /* вироджена: повертаємо велике скінченне число */
    }
    return max_abs / min_abs;
}

bool mag_cal_solve9(float a[9][9], const float b[9], float x[9]) {
    for (int i = 0; i < 9; i++) {
        x[i] = b[i];
    }

    /* Прямий хід із частковим вибором головного елемента */
    for (int i = 0; i < 9; i++) {
        int   pivot_row = i;
        float pivot_abs = fabsf(a[i][i]);
        for (int k = i + 1; k < 9; k++) {
            const float v = fabsf(a[k][i]);
            if (v > pivot_abs) { pivot_abs = v; pivot_row = k; }
        }

        /* Головний елемент зник навіть після перестановки — система вироджена */
        if (!(pivot_abs > 1e-8f)) {
            return false;
        }

        if (pivot_row != i) {
            for (int k = i; k < 9; k++) {
                const float t = a[i][k]; a[i][k] = a[pivot_row][k]; a[pivot_row][k] = t;
            }
            const float t = x[i]; x[i] = x[pivot_row]; x[pivot_row] = t;
        }

        const float inv_pivot = 1.0f / a[i][i];
        for (int k = i + 1; k < 9; k++) {
            const float factor = a[k][i] * inv_pivot;
            if (factor == 0.0f) continue;
            for (int j = i; j < 9; j++) {
                a[k][j] -= factor * a[i][j];
            }
            x[k] -= factor * x[i];
        }
    }

    /* Зворотний хід */
    for (int i = 8; i >= 0; i--) {
        float sum = x[i];
        for (int j = i + 1; j < 9; j++) {
            sum -= a[i][j] * x[j];
        }
        x[i] = sum / a[i][i];
        if (!isfinite(x[i])) {
            return false;
        }
    }
    return true;
}
