#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float w, x, y, z;
} quat_t;

typedef struct {
    vec3_t pos;        /* NED координати (метри) */
    vec3_t vel;        /* NED швидкість (м/с) */
    quat_t q;          /* Орієнтація Body -> NED */
    vec3_t gyro_bias;  /* Зміщення гіроскопа (рад/с) */
    vec3_t accel_bias; /* Зміщення акселерометра (м/с²) */
    float P[15];       /* Діагональ матриці коваріацій похибок */
} ekf_state_t;

void ekf_init(ekf_state_t *ekf) {
    ekf->pos = (vec3_t){0.0f, 0.0f, 0.0f};
    ekf->vel = (vec3_t){0.0f, 0.0f, 0.0f};
    ekf->q = (quat_t){1.0f, 0.0f, 0.0f, 0.0f};
    ekf->gyro_bias = (vec3_t){0.0f, 0.0f, 0.0f};
    ekf->accel_bias = (vec3_t){0.0f, 0.0f, 0.0f};

    /* Початкова дисперсія стану */
    for (int i = 0; i < 3; ++i) ekf->P[i] = 1.0f;       /* Позиція: 1 м² */
    for (int i = 3; i < 6; ++i) ekf->P[i] = 0.1f;      /* Швидкість: 0.1 (м/с)² */
    for (int i = 6; i < 9; ++i) ekf->P[i] = 0.001f;    /* Орієнтація: 0.001 рад² */
    for (int i = 9; i < 12; ++i) ekf->P[i] = 0.01f;    /* Зсув акселерометра */
    for (int i = 12; i < 15; ++i) ekf->P[i] = 0.0001f; /* Зсув гіроскопа */
}

/* Обертання вектора зі зв'язаної системи Body в систему NED */
vec3_t quat_rotate_vector(quat_t q, vec3_t v) {
    float t2 = q.w * q.x; float t3 = q.w * q.y; float t4 = q.w * q.z;
    float t5 = -q.x * q.x; float t6 = q.x * q.y; float t7 = q.x * q.z;
    float t8 = -q.y * q.y; float t9 = q.y * q.z; float t10 = -q.z * q.z;

    vec3_t out;
    out.x = 2.0f * ((t8 + t10) * v.x + (t6 - t4) * v.y + (t3 + t7) * v.z) + v.x;
    out.y = 2.0f * ((t4 + t6) * v.x + (t5 + t10) * v.y + (t9 - t2) * v.z) + v.y;
    out.z = 2.0f * ((t7 - t3) * v.x + (t2 + t9) * v.y + (t5 + t8) * v.z) + v.z;
    return out;
}

/* Крок передбачення стану (Predict) — викликається на кожній вибірці IMU (250 Гц) */
void ekf_predict_imu(ekf_state_t *ekf, vec3_t accel_raw, vec3_t gyro_raw, float dt) {
    const float GRAVITY_MSS = 9.80665f;

    /* 1. Компенсація оціненого зміщення нуля */
    vec3_t unbias_gyro = {
        gyro_raw.x - ekf->gyro_bias.x,
        gyro_raw.y - ekf->gyro_bias.y,
        gyro_raw.z - ekf->gyro_bias.z
    };
    vec3_t unbias_accel = {
        accel_raw.x - ekf->accel_bias.x,
        accel_raw.y - ekf->accel_bias.y,
        accel_raw.z - ekf->accel_bias.z
    };

    /* 2. Інтегрування орієнтації (кватерніонне числення) */
    float ha_x = 0.5f * unbias_gyro.x * dt;
    float ha_y = 0.5f * unbias_gyro.y * dt;
    float ha_z = 0.5f * unbias_gyro.z * dt;

    quat_t dq = {1.0f, ha_x, ha_y, ha_z};
    quat_t q_new = {
        ekf->q.w * dq.w - ekf->q.x * dq.x - ekf->q.y * dq.y - ekf->q.z * dq.z,
        ekf->q.w * dq.x + ekf->q.x * dq.w + ekf->q.y * dq.z - ekf->q.z * dq.y,
        ekf->q.w * dq.y - ekf->q.x * dq.z + ekf->q.y * dq.w + ekf->q.z * dq.x,
        ekf->q.w * dq.z + ekf->q.x * dq.y - ekf->q.y * dq.x + ekf->q.z * dq.w
    };

    /* Нормалізація кватерніона */
    float q_norm = sqrtf(q_new.w * q_new.w + q_new.x * q_new.x + q_new.y * q_new.y + q_new.z * q_new.z);
    if (q_norm > 1e-6f) {
        float inv = 1.0f / q_norm;
        ekf->q = (quat_t){q_new.w * inv, q_new.x * inv, q_new.y * inv, q_new.z * inv};
    }

    /* 3. Трансформація прискорення в NED та віднімання гравітації */
    vec3_t acc_ned = quat_rotate_vector(ekf->q, unbias_accel);
    acc_ned.z += GRAVITY_MSS; /* Гравітація спрямована вниз уздовж осі Down */

    /* 4. Інтегрування швидкості та координат */
    ekf->pos.x += ekf->vel.x * dt + 0.5f * acc_ned.x * dt * dt;
    ekf->pos.y += ekf->vel.y * dt + 0.5f * acc_ned.y * dt * dt;
    ekf->pos.z += ekf->vel.z * dt + 0.5f * acc_ned.z * dt * dt;

    ekf->vel.x += acc_ned.x * dt;
    ekf->vel.y += acc_ned.y * dt;
    ekf->vel.z += acc_ned.z * dt;

    /* 5. Поширення діагоналі коваріації шуму процесу */
    const float ACCEL_NOISE_VAR = 0.04f;    /* (м/с²)² */
    const float GYRO_NOISE_VAR = 0.0001f;   /* (рад/с)² */
    const float ACCEL_BIAS_VAR = 1e-6f;
    const float GYRO_BIAS_VAR = 1e-8f;

    for (int i = 0; i < 3; ++i) {
        ekf->P[i] += ekf->P[i + 3] * dt + 0.25f * ACCEL_NOISE_VAR * dt * dt;
        ekf->P[i + 3] += ACCEL_NOISE_VAR * dt;
        ekf->P[i + 6] += GYRO_NOISE_VAR * dt;
        ekf->P[i + 9] += ACCEL_BIAS_VAR * dt;
        ekf->P[i + 12] += GYRO_BIAS_VAR * dt;
    }
}

/* Крок корекції за GNSS (Update) — викликається при надходженні пакета PVT (5–10 Гц) */
void ekf_update_gnss(ekf_state_t *ekf, vec3_t gnss_pos, vec3_t gnss_vel, float pos_var, float vel_var) {
    /* Корекція позиції */
    for (int i = 0; i < 3; ++i) {
        float *p_est = (i == 0) ? &ekf->pos.x : ((i == 1) ? &ekf->pos.y : &ekf->pos.z);
        float p_meas = (i == 0) ? gnss_pos.x : ((i == 1) ? gnss_pos.y : gnss_pos.z);

        float innov = p_meas - *p_est;
        float S = ekf->P[i] + pos_var;
        float K = ekf->P[i] / S;

        *p_est += K * innov;
        ekf->P[i] *= (1.0f - K);
    }

    /* Корекція швидкості та оцінка зміщення акселерометра */
    for (int i = 0; i < 3; ++i) {
        float *v_est = (i == 0) ? &ekf->vel.x : ((i == 1) ? &ekf->vel.y : &ekf->vel.z);
        float v_meas = (i == 0) ? gnss_vel.x : ((i == 1) ? gnss_vel.y : gnss_vel.z);
        float *ba_est = (i == 0) ? &ekf->accel_bias.x : ((i == 1) ? &ekf->accel_bias.y : &ekf->accel_bias.z);

        float innov = v_meas - *v_est;
        float S = ekf->P[i + 3] + vel_var;
        float K_v = ekf->P[i + 3] / S;

        *v_est += K_v * innov;
        ekf->P[i + 3] *= (1.0f - K_v);

        /* Крос-корекція зміщення нуля акселерометра */
        float K_ba = 0.05f * (ekf->P[i + 9] / S);
        *ba_est -= K_ba * innov;
        ekf->P[i + 9] *= (1.0f - K_ba);
    }
}
