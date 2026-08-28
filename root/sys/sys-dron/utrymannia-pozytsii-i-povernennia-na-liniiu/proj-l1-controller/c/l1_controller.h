/* l1_controller.h - Модуль L1-навігації мовою C (C99) */
#ifndef L1_CONTROLLER_H
#define L1_CONTROLLER_H

#include <stdbool.h>
#include <math.h>

#define L1_GRAVITY 9.80665f
#define L1_PI      3.14159265358979323846f

typedef struct {
    float x;
    float y;
} l1_vec2_t;

typedef struct {
    float period_l1;       /* Бажаний період контуру T_L1 (типово 15.0..25.0 с) */
    float damping_ratio;   /* Коефіцієнт демпфування zeta (типово 0.7071) */
    float k_i;             /* Коефіцієнт інтегратора вітрового зносу (0.01..0.08) */
    float i_limit;         /* Максимальне накопичення інтеграла похибки (метри) */
    float roll_limit_rad;  /* Максимальний кут крену (радіани, типово 0.52 ~ 30 град) */
    float min_l1_dist;     /* Мінімальна довжина вектора L1 (метри, типово 15.0) */
    float max_l1_dist;     /* Максимальна довжина вектора L1 (метри, типово 200.0) */
} l1_params_t;

typedef struct {
    l1_params_t params;
    float integrator_ect;  /* Накопичений інтеграл похибки cross-track */
    float cross_track_err; /* Поточне бічне відхилення (метри) */
    float lookahead_dist;  /* Поточна розрахована довжина L1 (метри) */
    float accel_cmd;       /* Вихідне бокове прискорення a_s (м/с^2) */
    float roll_cmd;        /* Вихідний кут крену (радіани) */
} l1_state_t;

/* Ініціалізація структури контролера значеннями за замовчуванням */
void l1_init(l1_state_t* ctrl, float period_l1, float roll_limit_deg);

/* Скидання інтегратора (наприклад, при перемиканні точок місії) */
void l1_reset_integrator(l1_state_t* ctrl);

/* Розрахунок наведення на прямолінійний відрізок W_A -> W_B */
bool l1_update_line(l1_state_t* ctrl,
                    l1_vec2_t pos,
                    l1_vec2_t vel,
                    l1_vec2_t wa,
                    l1_vec2_t wb,
                    float dt);

/* Розрахунок наведення на коло радіуса radius навколо центру center */
bool l1_update_orbit(l1_state_t* ctrl,
                     l1_vec2_t pos,
                     l1_vec2_t vel,
                     l1_vec2_t center,
                     float radius,
                     bool clockwise,
                     float dt);

#endif /* L1_CONTROLLER_H */
