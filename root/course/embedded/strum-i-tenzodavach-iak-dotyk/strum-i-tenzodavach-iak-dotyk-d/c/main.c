#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define JOINTS_COUNT 3
#define WRENCH_AXES  6

/* Структура конфігурації та стану 6-осьового силомоментного давача */
typedef struct {
    float calib_matrix[WRENCH_AXES][WRENCH_AXES]; /* Калібрувальна матриця 6x6 */
    float tare_offset[WRENCH_AXES];               /* Зсув тари для кожного каналу */
    float counts_to_volts;                         /* Множник АЦП (Вольт / Count) */
} ForceTorqueSensor;

/* Структура силомоментного вектора (гвинта) */
typedef struct {
    float fx, fy, fz; /* Сили в Ньютонах */
    float mx, my, mz; /* Моменти в Ньютон-метрах */
} Wrench6D;

/* Структура спостерігача узагальненого імпульсу */
typedef struct {
    float k_i[JOINTS_COUNT];            /* Коефіцієнти підсилення спостерігача K_I */
    float integral_state[JOINTS_COUNT];  /* Акумулятор інтегратора */
    float p_prev[JOINTS_COUNT];         /* Попередній стан імпульсу M*dq */
    float r[JOINTS_COUNT];              /* Вектор поточної нев'язки r(t) ~ tau_ext */
    float base_threshold[JOINTS_COUNT]; /* Базовий поріг детектування зіткнення */
    float vel_threshold_gain[JOINTS_COUNT]; /* Чутливість порогу до швидкості */
} MomentumObserver;

/* Ініціалізація силомоментного давача */
void ft_sensor_init(ForceTorqueSensor* sensor, const float calib[WRENCH_AXES][WRENCH_AXES], float lsb_volts) {
    memcpy(sensor->calib_matrix, calib, sizeof(sensor->calib_matrix));
    sensor->counts_to_volts = lsb_volts;
    for (int i = 0; i < WRENCH_AXES; i++) {
        sensor->tare_offset[i] = 0.0f;
    }
}

/* Калібрування тари за сирими відліками АЦП у ненавантаженому стані */
void ft_sensor_tare(ForceTorqueSensor* sensor, const int32_t raw_adc[WRENCH_AXES]) {
    for (int i = 0; i < WRENCH_AXES; i++) {
        sensor->tare_offset[i] = (float)raw_adc[i] * sensor->counts_to_volts;
    }
}

/* Обчислення вектора сил і моментів через множення на калібрувальну матрицю */
Wrench6D ft_sensor_process(const ForceTorqueSensor* sensor, const int32_t raw_adc[WRENCH_AXES]) {
    float v_diff[WRENCH_AXES];
    float wrench_raw[WRENCH_AXES] = {0};

    for (int i = 0; i < WRENCH_AXES; i++) {
        v_diff[i] = ((float)raw_adc[i] * sensor->counts_to_volts) - sensor->tare_offset[i];
    }

    /* Матричне множення W = C * v_diff */
    for (int row = 0; row < WRENCH_AXES; row++) {
        for (int col = 0; col < WRENCH_AXES; col++) {
            wrench_raw[row] += sensor->calib_matrix[row][col] * v_diff[col];
        }
    }

    Wrench6D out;
    out.fx = wrench_raw[0];
    out.fy = wrench_raw[1];
    out.fz = wrench_raw[2];
    out.mx = wrench_raw[3];
    out.my = wrench_raw[4];
    out.mz = wrench_raw[5];
    return out;
}

/* Ініціалізація спостерігача імпульсу */
void momentum_observer_init(MomentumObserver* obs, const float gains[JOINTS_COUNT],
                            const float base_thr[JOINTS_COUNT], const float vel_gains[JOINTS_COUNT]) {
    for (int i = 0; i < JOINTS_COUNT; i++) {
        obs->k_i[i] = gains[i];
        obs->base_threshold[i] = base_thr[i];
        obs->vel_threshold_gain[i] = vel_gains[i];
        obs->integral_state[i] = 0.0f;
        obs->p_prev[i] = 0.0f;
        obs->r[i] = 0.0f;
    }
}

/* Крок оновлення спостерігача імпульсу та перевірка наявності зіткнення */
bool momentum_observer_update(MomentumObserver* obs,
                              const float q_vel[JOINTS_COUNT],
                              const float tau_cmd[JOINTS_COUNT],
                              const float mass_matrix[JOINTS_COUNT][JOINTS_COUNT],
                              const float coriolis_gravity[JOINTS_COUNT],
                              float dt) {
    bool collision_detected = false;
    float p_current[JOINTS_COUNT] = {0};

    /* Розрахунок узагальненого імпульсу p = M(q) * q_dot */
    for (int i = 0; i < JOINTS_COUNT; i++) {
        for (int j = 0; j < JOINTS_COUNT; j++) {
            p_current[i] += mass_matrix[i][j] * q_vel[j];
        }
    }

    /* Оновлення нев'язки r(t) через чисельне інтегрування за Ейлером */
    for (int i = 0; i < JOINTS_COUNT; i++) {
        /* Підінтегральний вираз: tau + C^T*q_dot - g + r */
        float integrand = tau_cmd[i] + coriolis_gravity[i] + obs->r[i];
        obs->integral_state[i] += integrand * dt;

        /* Нев'язка r_i(t) = K_I * [ p_i(t) - integral - p_i(0) ] */
        obs->r[i] = obs->k_i[i] * (p_current[i] - obs->integral_state[i]);

        /* Динамічний поріг детектування контакту */
        float dynamic_thr = obs->base_threshold[i] + obs->vel_threshold_gain[i] * fabsf(q_vel[i]);

        if (fabsf(obs->r[i]) > dynamic_thr) {
            collision_detected = true;
        }
        obs->p_prev[i] = p_current[i];
    }

    return collision_detected;
}
