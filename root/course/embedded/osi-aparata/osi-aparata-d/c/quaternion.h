#ifndef QUATERNION_H
#define QUATERNION_H

#include "linalg.h"

/* Одиничний кватерніон орієнтації, порядок пам'яті scalar-first: [w, x, y, z].
   Угода Гамільтона (i·j = k), поворот тіло -> світ. */
typedef struct { float w, x, y, z; } quat_t;

/* Кути Тейта-Браяна, радіани, послідовність Z-Y'-X". */
typedef struct { float roll, pitch, yaw; } euler_t;

quat_t quat_identity(void);
bool   quat_is_finite(quat_t q);
float  quat_norm(quat_t q);
quat_t quat_conj(quat_t q);
quat_t quat_mul(quat_t p, quat_t q);           /* добуток Гамільтона p ⊗ q */
quat_t quat_normalize(quat_t q);               /* точна, через sqrtf */
quat_t quat_normalize_fast(quat_t q);          /* ряд Тейлора 1-го порядку з відкатом */
quat_t quat_from_axis_angle(vec3_t axis, float angle_rad);
quat_t quat_from_rotation_vector(vec3_t phi);  /* експонента вектора повороту */
vec3_t quat_rotate(quat_t q, vec3_t v);        /* тіло -> світ */
vec3_t quat_rotate_inv(quat_t q, vec3_t v);    /* світ -> тіло */
quat_t quat_integrate_gyro(quat_t q, vec3_t omega, float dt); /* Ейлер 1-го порядку */
mat3_t quat_to_dcm(quat_t q);
euler_t quat_to_euler(quat_t q);
quat_t quat_from_euler(euler_t e);
quat_t quat_slerp(quat_t a, quat_t b, float t);
quat_t quat_nlerp(quat_t a, quat_t b, float t);

/* Кінематика кутів Ейлера. Повертає false у зоні шарнірного замка:
   множник 1/cos(θ) там не існує, і жодне число повернути чесно не можна. */
bool euler_rates_from_gyro(euler_t angles, vec3_t omega, euler_t *rates);

#endif /* QUATERNION_H */
