#include <stdint.h>
#include <stdbool.h>

#define NUM_ACTUATORS 4

typedef struct {
    float b_inv[NUM_ACTUATORS][4]; /* Псевдообернена матриця: рядки - мотори, стовпчики - [F_z, M_x, M_y, M_z] */
} mixer_config_t;

/* Обчислення виходів на ESC у діапазоні 0.0..1.0 з пріоритетною десатурацією */
void control_allocation_step(const mixer_config_t *cfg, 
                             float thrust, float roll, float pitch, float yaw,
                             float u_out[NUM_ACTUATORS])
{
    float u_thrust[NUM_ACTUATORS];
    float u_rp[NUM_ACTUATORS];
    float u_yaw[NUM_ACTUATORS];
    float u[NUM_ACTUATORS];

    /* 1. Роздільне проектування компонентів через псевдообернену матрицю */
    for (int i = 0; i < NUM_ACTUATORS; ++i) {
        u_thrust[i] = cfg->b_inv[i][0] * thrust;
        u_rp[i]     = cfg->b_inv[i][1] * roll + cfg->b_inv[i][2] * pitch;
        u_yaw[i]    = cfg->b_inv[i][3] * yaw;
        u[i]        = u_thrust[i] + u_rp[i] + u_yaw[i];
    }

    /* 2. Пошук екстремумів */
    float min_u = u[0], max_u = u[0];
    for (int i = 1; i < NUM_ACTUATORS; ++i) {
        if (u[i] < min_u) min_u = u[i];
        if (u[i] > max_u) max_u = u[i];
    }

    /* 3. Десатурація зсувом середньої тяги (Thrust Shift) */
    if (max_u > 1.0f) {
        float shift = max_u - 1.0f;
        for (int i = 0; i < NUM_ACTUATORS; ++i) u[i] -= shift;
        min_u -= shift;
        max_u = 1.0f;
    }
    if (min_u < 0.0f) {
        float shift = -min_u;
        for (int i = 0; i < NUM_ACTUATORS; ++i) u[i] += shift;
        max_u += shift;
        min_u = 0.0f;
    }

    /* 4. Якщо розмах перевищує 1.0, жертвуємо моментом рискання */
    if (max_u > 1.0f) {
        float max_rp = 0.0f;
        float max_y = 0.0f;
        for (int i = 0; i < NUM_ACTUATORS; ++i) {
            float abs_rp = u_rp[i] < 0.0f ? -u_rp[i] : u_rp[i];
            float abs_y  = u_yaw[i] < 0.0f ? -u_yaw[i] : u_yaw[i];
            if (abs_rp > max_rp) max_rp = abs_rp;
            if (abs_y > max_y) max_y = abs_y;
        }

        float yaw_margin = 0.5f - max_rp;
        if (yaw_margin < 0.0f) yaw_margin = 0.0f;

        float k_yaw = 1.0f;
        if (max_y > 1e-4f && max_y > yaw_margin) {
            k_yaw = yaw_margin / max_y;
        }

        /* Перерахунок команд з ослабленим рисканням */
        for (int i = 0; i < NUM_ACTUATORS; ++i) {
            u[i] = u_thrust[i] + u_rp[i] + u_yaw[i] * k_yaw;
        }

        /* Повторний зсув */
        max_u = u[0];
        for (int i = 1; i < NUM_ACTUATORS; ++i) {
            if (u[i] > max_u) max_u = u[i];
        }
        if (max_u > 1.0f) {
            float shift = max_u - 1.0f;
            for (int i = 0; i < NUM_ACTUATORS; ++i) u[i] -= shift;
        }
    }

    /* 5. Фінальний апаратний запобіжник [0.0, 1.0] */
    for (int i = 0; i < NUM_ACTUATORS; ++i) {
        if (u[i] < 0.0f) u[i] = 0.0f;
        if (u[i] > 1.0f) u[i] = 1.0f;
        u_out[i] = u[i];
    }
}
