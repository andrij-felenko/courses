#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define DEG_TO_RAD (0.017453292519943295f)
#define RAD_TO_DEG (57.29577951308232f)

/* Структура внутрішніх параметрів камери */
typedef struct {
    float fx;          /* Фокусна відстань по осі X (пікселі) */
    float fy;          /* Фокусна відстань по осі Y (пікселі) */
    float cx;          /* Головна точка кадру по осі X (пікселі) */
    float cy;          /* Головна точка кадру по осі Y (пікселі) */
} camera_intrinsics_t;

/* Обмежувальна рамка цілі на зображенні */
typedef struct {
    float u;           /* Центр рамки X (пікселі) */
    float v;           /* Центр рамки Y (пікселі) */
    float width;       /* Ширина рамки (пікселі) */
    float height;      /* Висота рамки (пікселі) */
    float confidence;  /* Достовірність детекції [0.0 ... 1.0] */
} target_bbox_t;

/* Розрахунок кутових похибок відхилення від оптичної осі */
bool compute_camera_angular_errors(const camera_intrinsics_t *cam,
                                   const target_bbox_t *bbox,
                                   float *err_yaw_rad,
                                   float *err_pitch_rad) {
    if (!cam || !bbox || !err_yaw_rad || !err_pitch_rad) {
        return false;
    }
    if (bbox->confidence < 0.5f) {
        return false;
    }

    float delta_u = bbox->u - cam->cx;
    float delta_v = bbox->v - cam->cy;

    /* Пінхол-модель: розрахунок кутових координат променя */
    *err_yaw_rad = atan2f(delta_u, cam->fx);
    *err_pitch_rad = atan2f(delta_v, cam->fy);

    return true;
}

/* Формування команди швидкості підвісу з ПД-регулятором та гірокомпенсацією */
void compute_gimbal_rate_command(float err_yaw, float err_pitch,
                                 float prev_err_yaw, float prev_err_pitch,
                                 float dt, float kp, float kd,
                                 float drone_gyro_yaw, float drone_gyro_pitch,
                                 float *cmd_yaw_rate, float *cmd_pitch_rate) {
    if (dt <= 0.0001f) {
        dt = 0.0333f;
    }

    float d_err_yaw = (err_yaw - prev_err_yaw) / dt;
    float d_err_pitch = (err_pitch - prev_err_pitch) / dt;

    /* ПД-керування з прямою компенсацією кутової швидкості носія */
    *cmd_yaw_rate = (kp * err_yaw + kd * d_err_yaw) - drone_gyro_yaw;
    *cmd_pitch_rate = (kp * err_pitch + kd * d_err_pitch) - drone_gyro_pitch;
}
