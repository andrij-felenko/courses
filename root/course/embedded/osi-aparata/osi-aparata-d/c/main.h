#ifndef GEOMETRY_TRANSFORMS_H
#define GEOMETRY_TRANSFORMS_H

#include <math.h>
#include <stdbool.h>

/* Тривимірний вектор */
typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

/* Одиничний кватерніон орієнтації [w, x, y, z] */
typedef struct {
    float w;
    float x;
    float y;
    float z;
} quat_t;

/* Матриця 3х3 (по рядках) */
typedef struct {
    float m[3][3];
} mat3_t;

/* Кути Ейлера Тейта-Браяна (радіани) */
typedef struct {
    float roll;   /* крен (phi)   */
    float pitch;  /* тангаж (theta) */
    float yaw;    /* курс (psi)   */
} euler_t;

/* Векторні базові операції */
static inline vec3_t vec3_add(vec3_t a, vec3_t b) {
    return (vec3_t){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline vec3_t vec3_sub(vec3_t a, vec3_t b) {
    return (vec3_t){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline vec3_t vec3_cross(vec3_t a, vec3_t b) {
    return (vec3_t){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/* Нормалізація кватерніона з апроксимацією Паде/Тейлора */
static inline quat_t quat_normalize_fast(quat_t q) {
    float sq_norm = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if (sq_norm < 1e-6f) {
        return (quat_t){1.0f, 0.0f, 0.0f, 0.0f};
    }
    /* Наближення 1/sqrt(norm) навколо 1.0 */
    float factor = 1.5f - 0.5f * sq_norm;
    return (quat_t){q.w * factor, q.x * factor, q.y * factor, q.z * factor};
}

/* Обертання вектора через кватерніон: v' = v + 2*q_vec x (q_vec x v + w*v) */
static inline vec3_t quat_rotate_vec3(quat_t q, vec3_t v) {
    vec3_t q_vec = {q.x, q.y, q.z};
    vec3_t t = vec3_cross(q_vec, v);
    t.x += q.w * v.x;
    t.y += q.w * v.y;
    t.z += q.w * v.z;
    
    vec3_t cross2 = vec3_cross(q_vec, t);
    return (vec3_t){
        v.x + 2.0f * cross2.x,
        v.y + 2.0f * cross2.y,
        v.z + 2.0f * cross2.z
    };
}

/* Інтегрування гіроскопа: dq/dt = 0.5 * q (x) [0, omega] */
static inline quat_t quat_integrate_gyro(quat_t q, vec3_t omega, float dt) {
    float half_dt = 0.5f * dt;
    quat_t delta_q = {
        .w = half_dt * (-q.x * omega.x - q.y * omega.y - q.z * omega.z),
        .x = half_dt * ( q.w * omega.x + q.y * omega.z - q.z * omega.y),
        .y = half_dt * ( q.w * omega.y - q.x * omega.z + q.z * omega.x),
        .z = half_dt * ( q.w * omega.z + q.x * omega.y - q.y * omega.x)
    };
    quat_t next_q = {
        q.w + delta_q.w,
        q.x + delta_q.x,
        q.y + delta_q.y,
        q.z + delta_q.z
    };
    return quat_normalize_fast(next_q);
}

/* Вилучення безпечних кутів Ейлера з кватерніона */
static inline euler_t quat_to_euler(quat_t q) {
    euler_t e;
    /* Крен (roll, навколо осі X) */
    float sinr_cosp = 2.0f * (q.w * q.x + q.y * q.z);
    float cosr_cosp = 1.0f - 2.0f * (q.x * q.x + q.y * q.y);
    e.roll = atan2f(sinr_cosp, cosr_cosp);

    /* Тангаж (pitch, навколо осі Y) із захистом від виходу з asin */
    float sinp = 2.0f * (q.w * q.y - q.z * q.x);
    if (sinp > 1.0f) sinp = 1.0f;
    if (sinp < -1.0f) sinp = -1.0f;
    e.pitch = asinf(sinp);

    /* Рискання (yaw, навколо осі Z) */
    float siny_cosp = 2.0f * (q.w * q.z + q.x * q.y);
    float cosy_cosp = 1.0f - 2.0f * (q.y * q.y + q.z * q.z);
    e.yaw = atan2f(siny_cosp, cosy_cosp);

    return e;
}

/* Множення матриці 3х3 на вектор 3х1 */
static inline vec3_t mat3_mul_vec3(mat3_t m, vec3_t v) {
    return (vec3_t){
        m.m[0][0] * v.x + m.m[0][1] * v.y + m.m[0][2] * v.z,
        m.m[1][0] * v.x + m.m[1][1] * v.y + m.m[1][2] * v.z,
        m.m[2][0] * v.x + m.m[2][1] * v.y + m.m[2][2] * v.z
    };
}

/* Повний конвеєр калібрування сенсора: v_body = R_board * R_align * S * (raw - bias) */
static inline vec3_t sensor_align_measurement(vec3_t raw, vec3_t bias, mat3_t scale_ortho,
                                              mat3_t r_align, mat3_t r_board) {
    vec3_t unbiased = vec3_sub(raw, bias);
    vec3_t scaled = mat3_mul_vec3(scale_ortho, unbiased);
    vec3_t aligned = mat3_mul_vec3(r_align, scaled);
    return mat3_mul_vec3(r_board, aligned);
}

#endif /* GEOMETRY_TRANSFORMS_H */
