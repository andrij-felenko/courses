#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define NUM_JOINTS 3
#define DT_SEC 0.001f

typedef enum {
    SAFETY_NORMAL = 0,
    SAFETY_WARNING_SLS,
    SAFETY_CONTROLLED_STOP_SS1,
    SAFETY_STO_TRIPPED
} safety_state_t;

typedef struct {
    float x_min, x_max;
    float y_min, y_max;
    float z_min, z_max;
} cartesian_box_t;

typedef struct {
    float max_joint_vel[NUM_JOINTS];
    float collision_threshold[NUM_JOINTS];
    float observer_gain_ki[NUM_JOINTS];
    cartesian_box_t allowed_zone;
} safety_config_t;

typedef struct {
    safety_config_t cfg;
    safety_state_t state;
    float momentum_integral[NUM_JOINTS];
    float residual[NUM_JOINTS];
    bool sto_relay_active;
} safety_watchdog_t;

/* Спрощена динамічна модель: матриця інерції M(q) для тестового вузла */
static void compute_dynamics(const float q[NUM_JOINTS], const float q_dot[NUM_JOINTS],
                             float M[NUM_JOINTS][NUM_JOINTS], float c_transpose_qdot[NUM_JOINTS],
                             float g[NUM_JOINTS]) {
    /* Базові діагональні інерції та перехресні зв'язки */
    M[0][0] = 2.5f + 0.8f * cosf(q[1]);
    M[0][1] = 0.4f * cosf(q[1]);
    M[0][2] = 0.0f;

    M[1][0] = M[0][1];
    M[1][1] = 1.2f + 0.3f * cosf(q[2]);
    M[1][2] = 0.15f * cosf(q[2]);

    M[2][0] = 0.0f;
    M[2][1] = M[1][2];
    M[2][2] = 0.5f;

    /* Коріолісові складові C^T(q, q_dot) * q_dot */
    c_transpose_qdot[0] = -0.4f * sinf(q[1]) * q_dot[1] * q_dot[0];
    c_transpose_qdot[1] =  0.4f * sinf(q[1]) * q_dot[0] * q_dot[0];
    c_transpose_qdot[2] =  0.0f;

    /* Гравітаційний вектор g(q) */
    g[0] = 0.0f;
    g[1] = 9.81f * 1.5f * cosf(q[0] + q[1]);
    g[2] = 9.81f * 0.5f * cosf(q[0] + q[1] + q[2]);
}

/* Пряма кінематика положення робочого інструмента (TCP) */
static void compute_forward_kinematics(const float q[NUM_JOINTS], float tcp[3]) {
    const float l1 = 0.4f, l2 = 0.35f, l3 = 0.15f;
    float a1 = q[0], a2 = q[0] + q[1], a3 = q[0] + q[1] + q[2];
    tcp[0] = l1 * cosf(a1) + l2 * cosf(a2) + l3 * cosf(a3);
    tcp[1] = l1 * sinf(a1) + l2 * sinf(a2) + l3 * sinf(a3);
    tcp[2] = 0.2f; /* Висота */
}

void safety_watchdog_init(safety_watchdog_t *wd, const safety_config_t *cfg) {
    memset(wd, 0, sizeof(*wd));
    wd->cfg = *cfg;
    wd->state = SAFETY_NORMAL;
    wd->sto_relay_active = false;
}

safety_state_t safety_watchdog_update(safety_watchdog_t *wd,
                                      const float q[NUM_JOINTS],
                                      const float q_dot[NUM_JOINTS],
                                      const float tau_measured[NUM_JOINTS]) {
    float M[NUM_JOINTS][NUM_JOINTS];
    float c_t_qdot[NUM_JOINTS];
    float g[NUM_JOINTS];
    float p[NUM_JOINTS];
    float tcp[3];
    int i, j;

    compute_dynamics(q, q_dot, M, c_t_qdot, g);
    compute_forward_kinematics(q, tcp);

    /* 1. Обчислення поточного імпульсу p = M * q_dot */
    for (i = 0; i < NUM_JOINTS; ++i) {
        p[i] = 0.0f;
        for (j = 0; j < NUM_JOINTS; ++j) {
            p[i] += M[i][j] * q_dot[j];
        }
    }

    /* 2. Оновлення спостерігача імпульсу: r = K_I * (p - integral) */
    bool collision_detected = false;
    for (i = 0; i < NUM_JOINTS; ++i) {
        float integrand = tau_measured[i] + c_t_qdot[i] - g[i] + wd->residual[i];
        wd->momentum_integral[i] += integrand * DT_SEC;
        wd->residual[i] = wd->cfg.observer_gain_ki[i] * (p[i] - wd->momentum_integral[i]);

        if (fabsf(wd->residual[i]) > wd->cfg.collision_threshold[i]) {
            collision_detected = true;
        }
    }

    /* 3. Перевірка обмеження швидкості осей (SLS) */
    bool speed_limit_violated = false;
    for (i = 0; i < NUM_JOINTS; ++i) {
        if (fabsf(q_dot[i]) > wd->cfg.max_joint_vel[i]) {
            speed_limit_violated = true;
        }
    }

    /* 4. Перевірка геофенсингу (Geofence Box) */
    bool geofence_violated = false;
    if (tcp[0] < wd->cfg.allowed_zone.x_min || tcp[0] > wd->cfg.allowed_zone.x_max ||
        tcp[1] < wd->cfg.allowed_zone.y_min || tcp[1] > wd->cfg.allowed_zone.y_max) {
        geofence_violated = true;
    }

    /* 5. Автомат безпечних станів */
    switch (wd->state) {
    case SAFETY_NORMAL:
        if (collision_detected) {
            wd->state = SAFETY_CONTROLLED_STOP_SS1;
        } else if (speed_limit_violated || geofence_violated) {
            wd->state = SAFETY_WARNING_SLS;
        }
        break;

    case SAFETY_WARNING_SLS:
        if (collision_detected) {
            wd->state = SAFETY_CONTROLLED_STOP_SS1;
        } else if (!speed_limit_violated && !geofence_violated) {
            wd->state = SAFETY_NORMAL;
        }
        break;

    case SAFETY_CONTROLLED_STOP_SS1:
        /* Після фіксації колізії привід гальмує і розмикає STO */
        wd->sto_relay_active = true;
        wd->state = SAFETY_STO_TRIPPED;
        break;

    case SAFETY_STO_TRIPPED:
        wd->sto_relay_active = true;
        break;
    }

    return wd->state;
}
