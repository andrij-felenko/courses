#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_ACTUATORS 16
#define NUM_AXES 6

typedef enum {
    ACTUATOR_TYPE_MOTOR = 0,
    ACTUATOR_TYPE_SERVO,
    ACTUATOR_TYPE_PUSHER,
    ACTUATOR_TYPE_TILT_MOTOR
} actuator_type_t;

typedef enum {
    AIRFRAME_MULTIROTOR = 0,
    AIRFRAME_FIXED_WING,
    AIRFRAME_VTOL_QUADPLANE,
    AIRFRAME_VTOL_TILTROTOR,
    AIRFRAME_ROVER_DIFF
} airframe_type_t;

/* Геометричний опис одиничного привода */
typedef struct {
    actuator_type_t type;
    float pos[3];       /* Положення r = [x, y, z] у системі FRD (метри) */
    float dir[3];       /* Одиничний вектор тяги n = [nx, ny, nz] */
    float c_thrust;     /* Коефіцієнт тяги / підйому */
    float c_torque;     /* Коефіцієнт реактивного моменту (+1 CCW, -1 CW) */
    float min_val;      /* Мінімальний сигнал (0.0 для мотора, -1.0 для руля) */
    float max_val;      /* Максимальний сигнал (1.0) */
} actuator_desc_t;

/* Конфігурація планера */
typedef struct {
    airframe_type_t type;
    size_t num_actuators;
    actuator_desc_t actuators[MAX_ACTUATORS];
    float v_min;        /* Початкова швидкість ефективності крила, м/с */
    float v_trans;      /* Швидкість завершення переходу, м/с */
} airframe_config_t;

/* Вхідний вектор віртуальних зусиль (Wrench) */
typedef struct {
    float f_x;          /* Поздовжня сила */
    float f_y;          /* Бічна сила */
    float f_z;          /* Вертикальна сила */
    float m_x;          /* Момент крену (Roll) */
    float m_y;          /* Момент тангажу (Pitch) */
    float m_z;          /* Момент рискання (Yaw) */
} wrench_setpoint_t;

/* Стан апарата для динамічного мікшування */
typedef struct {
    float v_ias;        /* Індикаторна повітряна швидкість, м/с */
    float tilt_rad;     /* Кут нахилу поворотних балок (0 - горизонт, PI/2 - вертикаль) */
} vehicle_state_t;

/* Обмежувач значення */
static inline float clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

/* Розрахунок вагового коефіцієнта переходу за квадратом швидкості */
float calculate_transition_weight(const airframe_config_t *cfg, float v_ias) {
    if (v_ias < cfg->v_min) return 0.0f;
    if (v_ias >= cfg->v_trans) return 1.0f;
    float v2 = v_ias * v_ias;
    float v_min2 = cfg->v_min * cfg->v_min;
    float v_trans2 = cfg->v_trans * cfg->v_trans;
    return (v2 - v_min2) / (v_trans2 - v_min2);
}

/* Розрахунок стовпчика матриці ефективності для конкретного привода */
void compute_actuator_column(const actuator_desc_t *act,
                             const vehicle_state_t *state,
                             float v_weight,
                             float col[NUM_AXES]) {
    memset(col, 0, sizeof(float) * NUM_AXES);

    switch (act->type) {
        case ACTUATOR_TYPE_MOTOR: {
            /* Несучий ротор мультикоптера (зникає при завершенні переходу) */
            float blend = 1.0f - v_weight;
            float nx = act->dir[0];
            float ny = act->dir[1];
            float nz = act->dir[2];

            /* Сили */
            col[0] = nx * act->c_thrust * blend;
            col[1] = ny * act->c_thrust * blend;
            col[2] = nz * act->c_thrust * blend;

            /* Моменти: r x F + Q */
            col[3] = (act->pos[1] * nz - act->pos[2] * ny) * act->c_thrust * blend;
            col[4] = (act->pos[2] * nx - act->pos[0] * nz) * act->c_thrust * blend;
            col[5] = ((act->pos[0] * ny - act->pos[1] * nx) * act->c_thrust +
                      nz * act->c_torque) * blend;
            break;
        }

        case ACTUATOR_TYPE_TILT_MOTOR: {
            /* Поворотний мотор: кут state->tilt_rad змінює орієнтацію тяги */
            float theta = state->tilt_rad;
            float ct = cosf(theta);
            float st = sinf(theta);

            /* Вектор тяги повертається від -Z (зависання) до +X (літак) */
            float fx = st * act->c_thrust;
            float fz = -ct * act->c_thrust;

            col[0] = fx;
            col[1] = 0.0f;
            col[2] = fz;

            /* Моменти сил відносно центра мас */
            col[3] = act->pos[1] * fz;
            col[4] = act->pos[2] * fx - act->pos[0] * fz;
            col[5] = -act->pos[1] * fx + act->c_torque * (-ct);
            break;
        }

        case ACTUATOR_TYPE_PUSHER: {
            /* Маршовий двигун для літакового польоту */
            col[0] = act->c_thrust; /* Створює тягу вперед F_x */
            col[4] = act->pos[2] * act->c_thrust; /* Плече тангажу */
            break;
        }

        case ACTUATOR_TYPE_SERVO: {
            /* Аеродинамічний руль (елерон/висота/напрямок), ефективність росте з w */
            float q_scale = 0.1f + 0.9f * v_weight;
            col[3] = act->dir[0] * act->c_thrust * q_scale; /* Roll authority */
            col[4] = act->dir[1] * act->c_thrust * q_scale; /* Pitch authority */
            col[5] = act->dir[2] * act->c_thrust * q_scale; /* Yaw authority */
            break;
        }
    }
}

/* Уніфікований конвеєр мікшування */
void mix_airframe_wrench(const airframe_config_t *cfg,
                         const vehicle_state_t *state,
                         const wrench_setpoint_t *sp,
                         float out_actuators[MAX_ACTUATORS]) {
    float v_weight = calculate_transition_weight(cfg, state->v_ias);
    float B[NUM_AXES][MAX_ACTUATORS];

    /* Побудова поточної матриці ефективності B */
    for (size_t j = 0; j < cfg->num_actuators; ++j) {
        float col[NUM_AXES];
        compute_actuator_column(&cfg->actuators[j], state, v_weight, col);
        for (size_t i = 0; i < NUM_AXES; ++i) {
            B[i][j] = col[i];
        }
    }

    /* Наближене розв'язання через транспоновану матрицю з нормалізацією */
    for (size_t j = 0; j < cfg->num_actuators; ++j) {
        float cmd = 0.0f;
        const actuator_desc_t *act = &cfg->actuators[j];

        if (act->type == ACTUATOR_TYPE_MOTOR || act->type == ACTUATOR_TYPE_TILT_MOTOR) {
            /* Базовий газ зависання (компенсація ваги F_z) */
            cmd += -sp->f_z * (-B[2][j]);
            /* Кутова стабілізація */
            cmd += sp->m_x * B[3][j];
            cmd += sp->m_y * B[4][j];
            cmd += sp->m_z * B[5][j];
        } else if (act->type == ACTUATOR_TYPE_PUSHER) {
            /* Пряме призначення тяги вперед */
            cmd = sp->f_x;
        } else if (act->type == ACTUATOR_TYPE_SERVO) {
            /* Відхилення аеродинамічних рулів */
            cmd += sp->m_x * B[3][j];
            cmd += sp->m_y * B[4][j];
            cmd += sp->m_z * B[5][j];
        }

        /* Пріоритетна десатурація та апаратні обмеження */
        out_actuators[j] = clampf(cmd, act->min_val, act->max_val);
    }
}

/* Демонстраційний тест */
int main(void) {
    /* Конфігурація QuadPlane: 4 підйомні ротори + 1 маршовий + 3 сервоприводи */
    airframe_config_t quadplane;
    quadplane.type = AIRFRAME_VTOL_QUADPLANE;
    quadplane.v_min = 8.0f;
    quadplane.v_trans = 16.0f;
    quadplane.num_actuators = 8;

    /* 4 підйомні мотори (X-конфігурація) */
    float arms[4][2] = {{0.3f, 0.3f}, {-0.3f, -0.3f}, {0.3f, -0.3f}, {-0.3f, 0.3f}};
    float cw_ccw[4] = {1.0f, 1.0f, -1.0f, -1.0f};

    for (int i = 0; i < 4; ++i) {
        quadplane.actuators[i].type = ACTUATOR_TYPE_MOTOR;
        quadplane.actuators[i].pos[0] = arms[i][0];
        quadplane.actuators[i].pos[1] = arms[i][1];
        quadplane.actuators[i].pos[2] = 0.0f;
        quadplane.actuators[i].dir[0] = 0.0f;
        quadplane.actuators[i].dir[1] = 0.0f;
        quadplane.actuators[i].dir[2] = -1.0f; /* Тяга вгору (-Z) */
        quadplane.actuators[i].c_thrust = 1.0f;
        quadplane.actuators[i].c_torque = 0.05f * cw_ccw[i];
        quadplane.actuators[i].min_val = 0.0f;
        quadplane.actuators[i].max_val = 1.0f;
    }

    /* Маршовий двигун */
    quadplane.actuators[4].type = ACTUATOR_TYPE_PUSHER;
    quadplane.actuators[4].c_thrust = 1.0f;
    quadplane.actuators[4].min_val = 0.0f;
    quadplane.actuators[4].max_val = 1.0f;

    /* Сервоприводи: елерон (Roll), висота (Pitch), напрямок (Yaw) */
    for (int i = 5; i < 8; ++i) {
        quadplane.actuators[i].type = ACTUATOR_TYPE_SERVO;
        memset(quadplane.actuators[i].dir, 0, sizeof(float)*3);
        quadplane.actuators[i].dir[i - 5] = 1.0f;
        quadplane.actuators[i].c_thrust = 1.0f;
        quadplane.actuators[i].min_val = -1.0f;
        quadplane.actuators[i].max_val = 1.0f;
    }

    wrench_setpoint_t setpoint = {
        .f_x = 0.6f,   /* Тяга вперед */
        .f_z = -1.0f,  /* Підтримка ваги */
        .m_x = 0.1f,   /* Корекція крену */
        .m_y = 0.0f,
        .m_z = 0.05f
    };

    printf("=== VTOL QuadPlane: Перевірка перехідного режиму ===\n");
    float test_speeds[] = {0.0f, 6.0f, 10.0f, 13.0f, 16.0f, 20.0f};

    for (size_t s = 0; s < sizeof(test_speeds)/sizeof(float); ++s) {
        vehicle_state_t state = {.v_ias = test_speeds[s], .tilt_rad = 0.0f};
        float outputs[MAX_ACTUATORS] = {0};

        mix_airframe_wrench(&quadplane, &state, &setpoint, outputs);
        float w = calculate_transition_weight(&quadplane, state.v_ias);

        printf("V_ias = %4.1f м/с | w_fw = %4.2f | Мотор 1: %4.2f | Марш: %4.2f | Елерон: %+4.2f\n",
               state.v_ias, w, outputs[0], outputs[4], outputs[5]);
    }

    return 0;
}
