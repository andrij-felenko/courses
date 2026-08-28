#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Тривимірний вектор
typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

// Одиничний кватерніон орієнтації
typedef struct {
    float w;
    float x;
    float y;
    float z;
} quat_t;

// Кути Ейлера (радіани)
typedef struct {
    float roll;
    float pitch;
    float yaw;
} euler_t;

// Повний навігаційний стан апарата
typedef struct {
    vec3_t  position_ned;   // метри
    vec3_t  velocity_ned;   // м/с
    quat_t  attitude;       // одиничний кватерніон B -> N
    vec3_t  angular_rate_b; // рад/с (p, q, r)
    vec3_t  accel_bias_b;   // м/с²
    vec3_t  gyro_bias_b;    // рад/с
} vehicle_state_t;

// Нормалізація кватерніона
static inline quat_t quat_normalize(quat_t q) {
    float sq = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if (sq < 1e-12f) {
        return (quat_t){ 1.0f, 0.0f, 0.0f, 0.0f };
    }
    float inv = 1.0f / sqrtf(sq);
    return (quat_t){ q.w * inv, q.x * inv, q.y * inv, q.z * inv };
}

// Крок чисельного інтегрування орієнтації за кутовою швидкістю (метод Ейлера)
quat_t quat_integrate(quat_t q, vec3_t omega, float dt) {
    float half_dt = 0.5f * dt;
    quat_t dq;
    dq.w = half_dt * (-q.x * omega.x - q.y * omega.y - q.z * omega.z);
    dq.x = half_dt * ( q.w * omega.x + q.y * omega.z - q.z * omega.y);
    dq.y = half_dt * ( q.w * omega.y - q.x * omega.z + q.z * omega.x);
    dq.z = half_dt * ( q.w * omega.z + q.x * omega.y - y * omega.x);

    quat_t next_q = {
        .w = q.w + dq.w,
        .x = q.x + dq.x,
        .y = q.y + dq.y,
        .z = q.z + dq.z
    };
    return quat_normalize(next_q);
}

// Поворот вектора з системи Body у систему NED (формула Родрігеса)
vec3_t quat_rotate_to_ned(quat_t q, vec3_t v) {
    // t = 2 * (q_vec x v)
    float tx = 2.0f * (q.y * v.z - q.z * v.y);
    float ty = 2.0f * (q.z * v.x - q.x * v.z);
    float tz = 2.0f * (q.x * v.y - q.y * v.x);

    // v_out = v + q.w * t + (q_vec x t)
    vec3_t out;
    out.x = v.x + q.w * tx + (q.y * tz - q.z * ty);
    out.y = v.y + q.w * ty + (q.z * tx - q.x * tz);
    out.z = v.z + q.w * tz + (q.x * ty - q.y * tx);
    return out;
}

// Перетворення кватерніона у кути Ейлера із захистом від NaN
euler_t quat_to_euler(quat_t q) {
    euler_t e;
    e.roll = atan2f(2.0f * (q.w * q.x + q.y * q.z), 1.0f - 2.0f * (q.x * q.x + q.y * q.y));

    float sin_pitch = 2.0f * (q.w * q.y - q.z * q.x);
    if (sin_pitch > 1.0f) {
        sin_pitch = 1.0f;
    } else if (sin_pitch < -1.0f) {
        sin_pitch = -1.0f;
    }
    e.pitch = asinf(sin_pitch);

    e.yaw = atan2f(2.0f * (q.w * q.z + q.x * q.y), 1.0f - 2.0f * (q.y * q.y + q.z * q.z));
    return e;
}
