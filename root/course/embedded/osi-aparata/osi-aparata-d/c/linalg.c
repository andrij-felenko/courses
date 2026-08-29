#include "linalg.h"

const mat3_t T_NED_ENU = { { { 0.0f, 1.0f,  0.0f },
                             { 1.0f, 0.0f,  0.0f },
                             { 0.0f, 0.0f, -1.0f } } };

static vec3_t row_of(mat3_t a, int i) {
    return vec3_make(a.m[i][0], a.m[i][1], a.m[i][2]);
}

static void set_row(mat3_t *a, int i, vec3_t v) {
    a->m[i][0] = v.x; a->m[i][1] = v.y; a->m[i][2] = v.z;
}

bool vec3_normalize(vec3_t v, vec3_t *out) {
    float n = vec3_norm(v);
    if (!out || !isfinite(n) || n < 1e-9f) return false;
    *out = vec3_scale(v, 1.0f / n);
    return true;
}

mat3_t mat3_identity(void) {
    mat3_t r = { { { 1.0f, 0.0f, 0.0f }, { 0.0f, 1.0f, 0.0f }, { 0.0f, 0.0f, 1.0f } } };
    return r;
}

vec3_t mat3_mul_vec3(mat3_t a, vec3_t v) {
    return vec3_make(a.m[0][0] * v.x + a.m[0][1] * v.y + a.m[0][2] * v.z,
                     a.m[1][0] * v.x + a.m[1][1] * v.y + a.m[1][2] * v.z,
                     a.m[2][0] * v.x + a.m[2][1] * v.y + a.m[2][2] * v.z);
}

mat3_t mat3_mul(mat3_t a, mat3_t b) {
    mat3_t r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = a.m[i][0] * b.m[0][j] + a.m[i][1] * b.m[1][j] + a.m[i][2] * b.m[2][j];
        }
    }
    return r;
}

mat3_t mat3_transpose(mat3_t a) {
    mat3_t r;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            r.m[i][j] = a.m[j][i];
    return r;
}

float mat3_det(mat3_t a) {
    return a.m[0][0] * (a.m[1][1] * a.m[2][2] - a.m[1][2] * a.m[2][1])
         - a.m[0][1] * (a.m[1][0] * a.m[2][2] - a.m[1][2] * a.m[2][0])
         + a.m[0][2] * (a.m[1][0] * a.m[2][1] - a.m[1][1] * a.m[2][0]);
}

mat3_t mat3_similarity(mat3_t r, mat3_t p) {
    return mat3_mul(mat3_mul(r, p), mat3_transpose(r));
}

float mat3_orthogonality_error(mat3_t r) {
    mat3_t e = mat3_mul(mat3_transpose(r), r);
    float worst = 0.0f;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            float ref = (i == j) ? 1.0f : 0.0f;
            float d = fabsf(e.m[i][j] - ref);
            if (d > worst) worst = d;
        }
    }
    return worst;
}

bool mat3_orthonormalize(mat3_t in, mat3_t *out) {
    if (!out) return false;
    vec3_t r0, r1;
    if (!vec3_normalize(row_of(in, 0), &r0)) return false;
    vec3_t tmp = row_of(in, 1);
    tmp = vec3_sub(tmp, vec3_scale(r0, vec3_dot(tmp, r0)));   /* прибираємо проекцію на перший рядок */
    if (!vec3_normalize(tmp, &r1)) return false;
    vec3_t r2 = vec3_cross(r0, r1);                            /* третій рядок добудовуємо правою трійкою */
    mat3_t res;
    set_row(&res, 0, r0);
    set_row(&res, 1, r1);
    set_row(&res, 2, r2);
    *out = res;
    return true;
}

vec3_t frame_swap_ned_enu(vec3_t v) {
    return mat3_mul_vec3(T_NED_ENU, v);
}

mat3_t frame_swap_cov_ned_enu(mat3_t p) {
    return mat3_similarity(T_NED_ENU, p);
}
