#ifndef LINALG_H
#define LINALG_H

#include <math.h>
#include <stdbool.h>

/* Вектор у довільному базисі: сенсора (S), тіла (B) або світу (N). */
typedef struct { float x, y, z; } vec3_t;

/* Матриця 3x3, зберігання по рядках: m[рядок][стовпець]. */
typedef struct { float m[3][3]; } mat3_t;

static inline vec3_t vec3_make(float x, float y, float z) {
    vec3_t v = { x, y, z };
    return v;
}
static inline vec3_t vec3_zero(void) { return vec3_make(0.0f, 0.0f, 0.0f); }
static inline vec3_t vec3_add(vec3_t a, vec3_t b) { return vec3_make(a.x + b.x, a.y + b.y, a.z + b.z); }
static inline vec3_t vec3_sub(vec3_t a, vec3_t b) { return vec3_make(a.x - b.x, a.y - b.y, a.z - b.z); }
static inline vec3_t vec3_scale(vec3_t a, float k) { return vec3_make(a.x * k, a.y * k, a.z * k); }
static inline float  vec3_dot(vec3_t a, vec3_t b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline vec3_t vec3_cross(vec3_t a, vec3_t b) {
    return vec3_make(a.y * b.z - a.z * b.y,
                     a.z * b.x - a.x * b.z,
                     a.x * b.y - a.y * b.x);
}
static inline float vec3_norm(vec3_t a) { return sqrtf(vec3_dot(a, a)); }
static inline bool vec3_is_finite(vec3_t a) {
    return isfinite(a.x) && isfinite(a.y) && isfinite(a.z);
}

/* Напрямку нульового вектора не існує — тому ознака успіху, а не мовчазне 0/0. */
bool vec3_normalize(vec3_t v, vec3_t *out);

mat3_t mat3_identity(void);
vec3_t mat3_mul_vec3(mat3_t a, vec3_t v);
mat3_t mat3_mul(mat3_t a, mat3_t b);
mat3_t mat3_transpose(mat3_t a);
float  mat3_det(mat3_t a);

/* Перенесення коваріації між базисами квадратичною формою: P' = R · P · Rᵀ. */
mat3_t mat3_similarity(mat3_t r, mat3_t p);

/* Найбільший за модулем елемент (RᵀR − I): скільки матриця втратила ортогональності. */
float  mat3_orthogonality_error(mat3_t r);

/* Грам-Шмідт по рядках: найближча ортонормована матриця. Хибно на виродженій. */
bool   mat3_orthonormalize(mat3_t in, mat3_t *out);

/* Стала матриця переходу NED <-> ENU. Обернена сама до себе: T·T = I. */
extern const mat3_t T_NED_ENU;
vec3_t frame_swap_ned_enu(vec3_t v);
mat3_t frame_swap_cov_ned_enu(mat3_t p);

#endif /* LINALG_H */
