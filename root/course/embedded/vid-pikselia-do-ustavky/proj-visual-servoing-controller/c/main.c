#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define M_PI_F 3.14159265358979323846f

/* ── Параметри камери та калібрування ───────────────────────────────────── */
typedef struct {
    float fx;           /* Фокусна відстань за X у пікселях */
    float fy;           /* Фокусна відстань за Y у пікселях */
    float cx;           /* Оптичний центр за X у пікселях */
    float cy;           /* Оптичний центр за Y у пікселях */
    float img_width;    /* Ширина зображення в пікселях */
    float img_height;   /* Висота зображення в пікселях */
} CameraIntrinsics;

/* ── Вимірювання від детектора (Bounding Box) ────────────────────────────── */
typedef struct {
    float u;            /* Координата X центра рамки (пікселі) */
    float v;            /* Координата Y центра рамки (пікселі) */
    float width;        /* Ширина рамки (пікселі) */
    float height;       /* Висота рамки (пікселі) */
    uint64_t timestamp_us; /* Мітка часу захоплення кадру сенсором (мкс) */
    bool valid;         /* Прапорець достовірності детекції */
} TargetDetection;

/* ── Стан фільтра Калмана для однієї осі (кут + кутова швидкість) ────────── */
typedef struct {
    float angle;        /* Оцінка кута візування (рад) */
    float rate;         /* Оцінка кутової швидкості цілі (рад/с) */
    float P[2][2];      /* Матриця коваріації похибок оцінки */
    float Q_angle;      /* Шум процесу за кутом */
    float Q_rate;       /* Шум процесу за кутовою швидкістю */
    float R_meas;       /* Шум вимірювання детектора */
    uint64_t last_update_us; /* Час останнього оновлення */
} KalmanAxis1D;

/* ── ПІД-регулятор для контуру візуального супроводу ─────────────────────── */
typedef struct {
    float kp;           /* Пропорційний коефіцієнт */
    float ki;           /* Інтегральний коефіцієнт */
    float kd;           /* Диференційний коефіцієнт */
    float integral;     /* Накопичена інтегральна помилка */
    float prev_meas;    /* Попереднє вимірювання для похідної */
    float max_integral; /* Межа інтегратора (anti-windup) */
    float max_output;   /* Максимальне значення вихідного сигналу */
    float deadband;     /* Зона нечутливості за похибкою */
    bool is_initialized;
} ServoingPID;

/* ── Вихідні уставки для автопілота ──────────────────────────────────────── */
typedef struct {
    float yaw_rate_rad_s;     /* Уставка кутової швидкості рискання */
    float pitch_rate_rad_s;   /* Уставка кутової швидкості тангажу */
    float forward_vel_m_s;    /* Уставка лінійної швидкості вперед */
    bool target_acquired;     /* Прапорець стабільного супроводу */
} GuidanceSetpoints;

/* ── Ініціалізація осі фільтра Калмана ───────────────────────────────────── */
void kalman_axis_init(KalmanAxis1D *k, float q_angle, float q_rate, float r_meas) {
    k->angle = 0.0f;
    k->rate = 0.0f;
    k->P[0][0] = 0.1f;
    k->P[0][1] = 0.0f;
    k->P[1][0] = 0.0f;
    k->P[1][1] = 1.0f;
    k->Q_angle = q_angle;
    k->Q_rate = q_rate;
    k->R_meas = r_meas;
    k->last_update_us = 0;
}

/* ── Крок прогнозу фільтра Калмана з компенсацією власного обертання ─────── */
void kalman_axis_predict(KalmanAxis1D *k, float dt, float gyro_rate_rad_s) {
    if (dt <= 0.0f || dt > 1.0f) return;

    /* Динаміка: кут цілі змінюється через швидкість цілі та власне обертання */
    float apparent_rate = k->rate - gyro_rate_rad_s;
    k->angle += apparent_rate * dt;

    /* Еволюція коваріації: P = F * P * F^T + Q */
    float P00 = k->P[0][0] + dt * (k->P[1][0] + k->P[0][1]) + dt * dt * k->P[1][1] + k->Q_angle * dt;
    float P01 = k->P[0][1] + dt * k->P[1][1];
    float P10 = k->P[1][0] + dt * k->P[1][1];
    float P11 = k->P[1][1] + k->Q_rate * dt;

    k->P[0][0] = P00;
    k->P[0][1] = P01;
    k->P[1][0] = P10;
    k->P[1][1] = P11;
}

/* ── Крок корекції фільтра Калмана новим вимірюванням ─────────────────────── */
void kalman_axis_update(KalmanAxis1D *k, float measured_angle) {
    /* Інновація (нев'язка) */
    float y = measured_angle - k->angle;

    /* Коваріація інновації: S = H * P * H^T + R = P00 + R */
    float S = k->P[0][0] + k->R_meas;
    if (fabsf(S) < 1e-6f) return;

    /* Коефіцієнти Калмана: K = P * H^T * inv(S) */
    float K0 = k->P[0][0] / S;
    float K1 = k->P[1][0] / S;

    /* Оновлення вектора стану */
    k->angle += K0 * y;
    k->rate  += K1 * y;

    /* Оновлення коваріації: P = (I - K * H) * P */
    float P00_new = (1.0f - K0) * k->P[0][0];
    float P01_new = (1.0f - K0) * k->P[0][1];
    float P10_new = k->P[1][0] - K1 * k->P[0][0];
    float P11_new = k->P[1][1] - K1 * k->P[0][1];

    k->P[0][0] = P00_new;
    k->P[0][1] = P01_new;
    k->P[1][0] = P10_new;
    k->P[1][1] = P11_new;
}

/* ── Екстраполяція стану вперед на час транспортної затримки T_lat ───────── */
void kalman_axis_extrapolate(const KalmanAxis1D *k, float latency_s, float *out_angle, float *out_rate) {
    if (out_angle) {
        *out_angle = k->angle + k->rate * latency_s;
    }
    if (out_rate) {
        *out_rate = k->rate;
    }
}

/* ── Ініціалізація ПІД-регулятора ────────────────────────────────────────── */
void pid_init(ServoingPID *pid, float kp, float ki, float kd, float max_out, float max_i, float deadband) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->max_output = max_out;
    pid->max_integral = max_i;
    pid->deadband = deadband;
    pid->integral = 0.0f;
    pid->prev_meas = 0.0f;
    pid->is_initialized = false;
}

/* ── Обчислення виходу ПІД-регулятора ────────────────────────────────────── */
float pid_update(ServoingPID *pid, float error, float measured_val, float dt) {
    if (dt <= 0.0f) return 0.0f;

    /* Застосування зони нечутливості */
    if (fabsf(error) < pid->deadband) {
        error = 0.0f;
    }

    /* Пропорційна складова */
    float p_term = pid->kp * error;

    /* Інтегральна складова з обмеженням (anti-windup) */
    pid->integral += error * dt;
    if (pid->integral > pid->max_integral) {
        pid->integral = pid->max_integral;
    } else if (pid->integral < -pid->max_integral) {
        pid->integral = -pid->max_integral;
    }
    float i_term = pid->ki * pid->integral;

    /* Диференційна складова за вимірюванням (уникає derivative kick) */
    float d_term = 0.0f;
    if (pid->is_initialized) {
        float d_meas = (measured_val - pid->prev_meas) / dt;
        d_term = -pid->kd * d_meas;
    } else {
        pid->is_initialized = true;
    }
    pid->prev_meas = measured_val;

    /* Формування та обмеження загального виходу */
    float output = p_term + i_term + d_term;
    if (output > pid->max_output) {
        output = pid->max_output;
    } else if (output < -pid->max_output) {
        output = -pid->max_output;
    }

    return output;
}

/* ── Контролер візуального наведення в цілому ────────────────────────────── */
typedef struct {
    CameraIntrinsics camera;
    KalmanAxis1D kf_yaw;
    KalmanAxis1D kf_pitch;
    ServoingPID pid_yaw;
    ServoingPID pid_pitch;
    ServoingPID pid_forward;
    float desired_bbox_scale;  /* Бажаний розмір об'єкта sqrt(w*h) */
    uint64_t last_frame_time_us;
    uint64_t last_exec_time_us;
    bool target_tracked;
} VisualGuidanceController;

void visual_guidance_init(VisualGuidanceController *c, const CameraIntrinsics *cam) {
    c->camera = *cam;
    kalman_axis_init(&c->kf_yaw, 0.01f, 0.5f, 0.005f);
    kalman_axis_init(&c->kf_pitch, 0.01f, 0.5f, 0.005f);

    /* Налаштування коефіцієнтів ПІД (кутові швидкості обмежені 1.0 рад/с) */
    pid_init(&c->pid_yaw, 1.8f, 0.1f, 0.15f, 1.0f, 0.3f, 0.008f);
    pid_init(&c->pid_pitch, 1.8f, 0.1f, 0.15f, 0.8f, 0.2f, 0.008f);
    pid_init(&c->pid_forward, 0.02f, 0.001f, 0.005f, 3.0f, 0.5f, 2.0f);

    c->desired_bbox_scale = 80.0f; /* 80 пікселів за геометричним середнім */
    c->last_frame_time_us = 0;
    c->last_exec_time_us = 0;
    c->target_tracked = false;
}

/* ── Обробка нового кадру від детектора ──────────────────────────────────── */
void visual_guidance_on_detection(VisualGuidanceController *c, const TargetDetection *det) {
    if (!det->valid) {
        c->target_tracked = false;
        return;
    }

    /* Перетворення координат пікселів у кутові похибки за моделлю камери */
    float norm_x = (det->u - c->camera.cx) / c->camera.fx;
    float norm_y = (det->v - c->camera.cy) / c->camera.fy;

    float angle_yaw_meas = atanf(norm_x);
    float angle_pitch_meas = atanf(norm_y);

    /* Корекція фільтрів Калмана */
    kalman_axis_update(&c->kf_yaw, angle_yaw_meas);
    kalman_axis_update(&c->kf_pitch, angle_pitch_meas);

    c->last_frame_time_us = det->timestamp_us;
    c->target_tracked = true;
}

/* ── Високочастотний цикл керування (виклик з частотою контуру автопілота) ─ */
void visual_guidance_update(VisualGuidanceController *c,
                            uint64_t current_time_us,
                            float gyro_yaw_rad_s,
                            float gyro_pitch_rad_s,
                            float current_bbox_scale,
                            GuidanceSetpoints *out_sp) {
    if (!c->target_tracked || c->last_exec_time_us == 0) {
        c->last_exec_time_us = current_time_us;
        out_sp->yaw_rate_rad_s = 0.0f;
        out_sp->pitch_rate_rad_s = 0.0f;
        out_sp->forward_vel_m_s = 0.0f;
        out_sp->target_acquired = false;
        return;
    }

    float dt_exec = (float)(current_time_us - c->last_exec_time_us) * 1e-6f;
    c->last_exec_time_us = current_time_us;

    /* 1. Крок прогнозу фільтра Калмана за часом циклу та гіроскопами */
    kalman_axis_predict(&c->kf_yaw, dt_exec, gyro_yaw_rad_s);
    kalman_axis_predict(&c->kf_pitch, dt_exec, gyro_pitch_rad_s);

    /* 2. Оцінка повної затримки кадру (t_now - t_capture) */
    float latency_s = (float)(current_time_us - c->last_frame_time_us) * 1e-6f;
    if (latency_s > 0.5f) {
        /* Якщо кадри не надходили більше 500 мс — втрата супроводу */
        c->target_tracked = false;
        out_sp->target_acquired = false;
        return;
    }

    /* 3. Екстраполяція положення цілі на поточний момент часу */
    float est_yaw_angle, est_yaw_rate;
    float est_pitch_angle, est_pitch_rate;
    kalman_axis_extrapolate(&c->kf_yaw, latency_s, &est_yaw_angle, &est_yaw_rate);
    kalman_axis_extrapolate(&c->kf_pitch, latency_s, &est_pitch_angle, &est_pitch_rate);

    /* 4. Формування уставок ПІД-регулятором (ціль тримаємо в центрі: e = -angle) */
    float err_yaw = est_yaw_angle;
    float err_pitch = est_pitch_angle;

    out_sp->yaw_rate_rad_s = pid_update(&c->pid_yaw, err_yaw, est_yaw_angle, dt_exec);
    /* Тангаж: зміщення вниз (позитивний v) вимагає нахилу носа вниз (позитивна уставка) */
    out_sp->pitch_rate_rad_s = -pid_update(&c->pid_pitch, err_pitch, est_pitch_angle, dt_exec);

    /* 5. Уставка швидкості вперед за похибкою масштабу цілі */
    if (current_bbox_scale > 5.0f) {
        float err_scale = c->desired_bbox_scale - current_bbox_scale;
        out_sp->forward_vel_m_s = pid_update(&c->pid_forward, err_scale, current_bbox_scale, dt_exec);
    } else {
        out_sp->forward_vel_m_s = 0.0f;
    }

    out_sp->target_acquired = true;
}
