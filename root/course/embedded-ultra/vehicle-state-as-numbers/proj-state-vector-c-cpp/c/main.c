#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Базовий 3D вектор (IEEE-754 single precision float)
typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

// Одиничний кватерніон Гамільтона q = [w, x, y, z]
typedef struct {
    float w;
    float x;
    float y;
    float z;
} quat_t;

// Кути орієнтації Ейлера (крен, тангаж, курс у радіанах)
typedef struct {
    float roll;
    float pitch;
    float yaw;
} euler_t;

// Повний просторовий стан літального апарата
typedef struct {
    vec3_t  position_ned;   // Координати в земній системі NED (метри)
    vec3_t  velocity_ned;   // Швидкість у земній системі NED (м/с)
    quat_t  attitude;       // Орієнтація корпусу відносно NED (Body -> NED)
    vec3_t  angular_rate_b; // Кутові швидкості гіроскопа (рад/с)
    vec3_t  linear_accel_b; // Виміряне перевантаження акселерометра (м/с²)
    vec3_t  gyro_bias_b;    // Оцінка зміщення нуля гіроскопа (рад/с)
    vec3_t  accel_bias_b;   // Оцінка зміщення нуля акселерометра (м/с²)
} vehicle_state_t;

// Ініціалізація стану системи
void vehicle_state_init(vehicle_state_t *state) {
    if (!state) return;
    state->position_ned = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->velocity_ned = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->attitude = (quat_t){ 1.0f, 0.0f, 0.0f, 0.0f };
    state->angular_rate_b = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->linear_accel_b = (vec3_t){ 0.0f, 0.0f, -9.80665f };
    state->gyro_bias_b = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->accel_bias_b = (vec3_t){ 0.0f, 0.0f, 0.0f };
}

// Нормалізація кватерніона орієнтації
quat_t quat_normalize(quat_t q) {
    float norm_sq = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if (norm_sq < 1e-12f) {
        return (quat_t){ 1.0f, 0.0f, 0.0f, 0.0f };
    }
    float inv_norm = 1.0f / sqrtf(norm_sq);
    return (quat_t){
        .w = q.w * inv_norm,
        .x = q.x * inv_norm,
        .y = q.y * inv_norm,
        .z = q.z * inv_norm
    };
}

// Крок інтегрування орієнтації методом Рунге-Кутти 2-го порядку (RK2)
quat_t quat_integrate_rk2(quat_t q, vec3_t omega, float dt) {
    float h = 0.5f * dt;

    // k1 = 0.5 * q * omega
    quat_t k1;
    k1.w = 0.5f * (-q.x * omega.x - q.y * omega.y - q.z * omega.z);
    k1.x = 0.5f * ( q.w * omega.x + q.y * omega.z - q.z * omega.y);
    k1.y = 0.5f * ( q.w * omega.y - q.x * omega.z + q.z * omega.x);
    k1.z = 0.5f * ( q.w * omega.z + q.x * omega.y - y * omega.x);

    // Проміжний кватерніон q_mid = q + k1 * (dt/2)
    quat_t q_mid = {
        .w = q.w + k1.w * h,
        .x = q.x + k1.x * h,
        .y = q.y + k1.y * h,
        .z = q.z + k1.z * h
    };
    q_mid = quat_normalize(q_mid);

    // k2 = 0.5 * q_mid * omega
    quat_t k2;
    k2.w = 0.5f * (-q_mid.x * omega.x - q_mid.y * omega.y - q_mid.z * omega.z);
    k2.x = 0.5f * ( q_mid.w * omega.x + q_mid.y * omega.z - q_mid.z * omega.y);
    k2.y = 0.5f * ( q_mid.w * omega.y - q_mid.x * omega.z + q_mid.z * omega.x);
    k2.z = 0.5f * ( q_mid.w * omega.z + q_mid.x * omega.y - q_mid.y * omega.x);

    // Фінальне оновлення q_next = q + k2 * dt
    quat_t q_next = {
        .w = q.w + k2.w * dt,
        .x = q.x + k2.x * dt,
        .y = q.y + k2.y * dt,
        .z = q.z + k2.z * dt
    };
    return quat_normalize(q_next);
}

// Обертання вектора із Body у NED за формулою Родрігеса
vec3_t quat_rotate_body_to_ned(quat_t q, vec3_t v) {
    float tx = 2.0f * (q.y * v.z - q.z * v.y);
    float ty = 2.0f * (q.z * v.x - q.x * v.z);
    float tz = 2.0f * (q.x * v.y - q.y * v.x);

    vec3_t res;
    res.x = v.x + q.w * tx + (q.y * tz - q.z * ty);
    res.y = v.y + q.w * ty + (q.z * tx - q.x * tz);
    res.z = v.z + q.w * tz + (q.x * ty - q.y * tx);
    return res;
}

// Перетворення кватерніона у кути Ейлера (радіани)
euler_t quat_to_euler_angles(quat_t q) {
    euler_t e;
    e.roll = atan2f(2.0f * (q.w * q.x + q.y * q.z), 1.0f - 2.0f * (q.x * q.x + q.y * q.y));

    float sin_pitch = 2.0f * (q.w * q.y - q.z * q.x);
    if (sin_pitch > 1.0f) sin_pitch = 1.0f;
    if (sin_pitch < -1.0f) sin_pitch = -1.0f;
    e.pitch = asinf(sin_pitch);

    e.yaw = atan2f(2.0f * (q.w * q.z + q.x * q.y), 1.0f - 2.0f * (q.y * q.y + q.z * q.z));
    return e;
}

// Крок комплексного оновлення кінематики стану
void vehicle_state_update_imu(vehicle_state_t *state, vec3_t gyro_raw, vec3_t accel_raw, float dt) {
    if (!state || dt <= 0.0f) return;

    // Компенсація калібрувальних зміщень
    state->angular_rate_b.x = gyro_raw.x - state->gyro_bias_b.x;
    state->angular_rate_b.y = gyro_raw.y - state->gyro_bias_b.y;
    state->angular_rate_b.z = gyro_raw.z - state->gyro_bias_b.z;

    vec3_t accel_corr = {
        .x = accel_raw.x - state->accel_bias_b.x,
        .y = accel_raw.y - state->accel_bias_b.y,
        .z = accel_raw.z - state->accel_bias_b.z
    };
    state->linear_accel_b = accel_corr;

    // 1. Інтегрування орієнтації
    state->attitude = quat_integrate_rk2(state->attitude, state->angular_rate_b, dt);

    // 2. Обертання прискорення в NED та віднімання гравітації g = 9.80665 м/с²
    vec3_t accel_ned = quat_rotate_body_to_ned(state->attitude, accel_corr);
    accel_ned.z += 9.80665f; // у системі NED вісь Z вниз, гравітація додається до питомої сили

    // 3. Інтегрування швидкості та координат
    state->velocity_ned.x += accel_ned.x * dt;
    state->velocity_ned.y += accel_ned.y * dt;
    state->velocity_ned.z += accel_ned.z * dt;

    state->position_ned.x += state->velocity_ned.x * dt;
    state->position_ned.y += state->velocity_ned.y * dt;
    state->position_ned.z += state->velocity_ned.z * dt;
}
