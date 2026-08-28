/* ============================================================================
 * control_allocator.h / control_allocator.c
 * Модуль матричного розподілу керування польотного контролера (C99)
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_AXES 4          /* F_z (тяга), M_x (крен), M_y (тангаж), M_z (рискання) */
#define MAX_ACTUATORS 8     /* До 8 моторів/сервоприводів */

typedef struct {
    uint8_t num_actuators;                          /* Кількість фізичних приводів (наприклад, 4, 6, 8) */
    float b_pseudo_inv[MAX_ACTUATORS][MAX_AXES];    /* Псевдообернена матриця B^+ */
    float u_min[MAX_ACTUATORS];                     /* Нижня межа привода (наприклад, 0.0 для ESC) */
    float u_max[MAX_ACTUATORS];                     /* Верхня межа привода (наприклад, 1.0 для ESC) */
    float yaw_weight;                               /* Вага збереження рискання (0.0..1.0) */
} allocator_config_t;

typedef struct {
    allocator_config_t config;
    bool saturated;                                 /* Прапорець настання насичення */
} allocator_t;

/* Ініціалізація алокатора конфігурацією */
void allocator_init(allocator_t *alloc, const allocator_config_t *cfg)
{
    if (!alloc || !cfg) return;
    memcpy(&alloc->config, cfg, sizeof(allocator_config_t));
    alloc->saturated = false;
}

/* Обчислення фізичних сигналів приводів u з віртуальних зусиль tau */
void allocator_update(allocator_t *alloc, const float tau[MAX_AXES], float u_out[MAX_ACTUATORS])
{
    if (!alloc || !tau || !u_out) return;

    const uint8_t n_act = alloc->config.num_actuators;
    float u[MAX_ACTUATORS];
    float u_thrust[MAX_ACTUATORS];
    float u_rp[MAX_ACTUATORS];
    float u_yaw[MAX_ACTUATORS];

    /* Крок 1: Роздільний розрахунок компонентів для кожного привода */
    for (uint8_t i = 0; i < n_act; ++i) {
        u_thrust[i] = alloc->config.b_pseudo_inv[i][0] * tau[0]; /* Внесок F_z */
        u_rp[i]     = alloc->config.b_pseudo_inv[i][1] * tau[1] +
                      alloc->config.b_pseudo_inv[i][2] * tau[2]; /* Внесок M_x, M_y */
        u_yaw[i]    = alloc->config.b_pseudo_inv[i][3] * tau[3]; /* Внесок M_z */
        u[i]        = u_thrust[i] + u_rp[i] + u_yaw[i];
    }

    /* Крок 2: Пошук мінімуму та максимуму */
    float min_val = u[0];
    float max_val = u[0];
    for (uint8_t i = 1; i < n_act; ++i) {
        if (u[i] < min_val) min_val = u[i];
        if (u[i] > max_val) max_val = u[i];
    }

    alloc->saturated = (max_val > 1.0f || min_val < 0.0f);

    /* Крок 3: Десатурація зсувом (Shift Desaturation) */
    if (max_val > 1.0f) {
        float shift = max_val - 1.0f;
        for (uint8_t i = 0; i < n_act; ++i) u[i] -= shift;
        min_val -= shift;
        max_val = 1.0f;
    }

    if (min_val < 0.0f) {
        float shift = -min_val;
        for (uint8_t i = 0; i < n_act; ++i) u[i] += shift;
        max_val += shift;
        min_val = 0.0f;
    }

    /* Крок 4: Якщо після зсуву розмах (max - min) перевищує 1.0, жертвуємо рисканням */
    if (max_val > 1.0f) {
        /* Зменшуємо внесок yaw */
        float yaw_scale = 1.0f;
        float max_rp = 0.0f;
        for (uint8_t i = 0; i < n_act; ++i) {
            float abs_rp = u_rp[i] < 0.0f ? -u_rp[i] : u_rp[i];
            if (abs_rp > max_rp) max_rp = abs_rp;
        }

        /* Залишок під yaw = 0.5 - max_rp */
        float yaw_headroom = 0.5f - max_rp;
        if (yaw_headroom < 0.0f) yaw_headroom = 0.0f;

        float max_yaw = 0.0f;
        for (uint8_t i = 0; i < n_act; ++i) {
            float abs_y = u_yaw[i] < 0.0f ? -u_yaw[i] : u_yaw[i];
            if (abs_y > max_yaw) max_yaw = abs_y;
        }

        if (max_yaw > 1e-4f && max_yaw > yaw_headroom) {
            yaw_scale = yaw_headroom / max_yaw;
        }

        /* Перерахунок з відмасштабованим yaw */
        for (uint8_t i = 0; i < n_act; ++i) {
            u[i] = u_thrust[i] + u_rp[i] + u_yaw[i] * yaw_scale;
        }

        /* Повторний зсув після стиснення yaw */
        min_val = u[0];
        max_val = u[0];
        for (uint8_t i = 1; i < n_act; ++i) {
            if (u[i] < min_val) min_val = u[i];
            if (u[i] > max_val) max_val = u[i];
        }
        if (max_val > 1.0f) {
            float shift = max_val - 1.0f;
            for (uint8_t i = 0; i < n_act; ++i) u[i] -= shift;
        }
    }

    /* Крок 5: Апаратне обмеження [u_min, u_max] */
    for (uint8_t i = 0; i < n_act; ++i) {
        float lo = alloc->config.u_min[i];
        float hi = alloc->config.u_max[i];
        if (u[i] < lo) u[i] = lo;
        if (u[i] > hi) u[i] = hi;
        u_out[i] = u[i];
    }
}
