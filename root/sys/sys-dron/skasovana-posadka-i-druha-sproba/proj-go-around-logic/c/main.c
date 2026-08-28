#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define GO_AROUND_DT_S 0.02f                  /* Період оновлення 50 Гц (20 мс) */
#define DEFAULT_MAX_ATTEMPTS 2U               /* Максимальна кількість спроб */
#define LIDAR_CONFIRM_TICKS 5U                /* 5 циклів * 20 мс = 100 мс фільтр */
#define GRAVITY_MSS 9.80665f

typedef enum {
    GA_STATE_APPROACH_DESCENT = 0,
    GA_STATE_ABORT_BRAKE_CLIMB,
    GA_STATE_ENERGY_AUDIT,
    GA_STATE_CIRCUIT_LOITER,
    GA_STATE_EMERGENCY_FAILSAFE
} ga_state_t;

typedef struct {
    float max_thrust_to_weight;   /* Тягооснащеність, наприклад 1.8 */
    float motor_spoolup_time_s;   /* Час розкрутки моторів, наприклад 0.20 с */
    float safety_margin_m;        /* Запас висоти над просадкою, наприклад 0.8 м */
    float missed_approach_alt_m;  /* Безпечний ешелон відходу, наприклад 25.0 м */
    float obstacle_dist_thresh_m; /* Поріг виявлення перешкоди лідаром, наприклад 1.5 м */
    float max_tilt_angle_rad;     /* Граничний кут нахилу, наприклад 0.436 рад (25 град) */
    float min_soc_for_retry;      /* Мінімальний SOC для другої спроби, наприклад 0.22 */
    float min_cell_voltage_v;     /* Мінімальна напруга банки під навантаженням, наприклад 3.35 В */
    uint8_t cell_count;           /* Кількість послідовних банок (наприклад, 6 для 6S) */
    uint8_t max_attempts;         /* Ліміт повторних спроб */
    uint32_t loiter_duration_ms;  /* Тривалість кружляння перед повторним заходом */
} ga_config_t;

typedef struct {
    float altitude_m;
    float vertical_speed_ms;      /* Від'ємна при спуску */
    float lidar_distance_m;
    float roll_rad;
    float pitch_rad;
    float battery_voltage_v;
    float battery_current_a;
    float battery_soc;            /* 0.0 .. 1.0 */
    bool lidar_valid;
    bool operator_abort_req;
} ga_telemetry_t;

typedef struct {
    float target_alt_m;
    float target_vz_ms;
    float target_roll_rad;
    float target_pitch_rad;
    float max_tilt_limit_rad;
    bool climb_priority;
    bool emergency_land_now;
} ga_setpoints_t;

typedef struct {
    ga_state_t state;
    uint8_t attempt_counter;
    uint8_t lidar_obstacle_counter;
    uint32_t state_timer_ms;
    ga_config_t config;
    ga_setpoints_t setpoints;
} ga_fsm_t;

/* Розрахунок динамічної просадки */
static float calculate_sinkage(float v_z, float thrust_ratio, float spool_time) {
    if (v_z >= 0.0f) {
        return 0.0f;
    }
    float abs_vz = fabsf(v_z);
    float a_climb = (thrust_ratio - 1.0f) * GRAVITY_MSS;
    if (a_climb < 1.0f) {
        a_climb = 1.0f; /* Захист від ділення на нуль при слабкій тязі */
    }
    float h_spool = abs_vz * spool_time;
    float h_brake = (abs_vz * abs_vz) / (2.0f * a_climb);
    return h_spool + h_brake;
}

/* Ініціалізація автомата */
void ga_fsm_init(ga_fsm_t *fsm, const ga_config_t *cfg) {
    if (cfg != NULL) {
        fsm->config = *cfg;
    } else {
        fsm->config.max_thrust_to_weight = 1.8f;
        fsm->config.motor_spoolup_time_s = 0.20f;
        fsm->config.safety_margin_m = 0.8f;
        fsm->config.missed_approach_alt_m = 25.0f;
        fsm->config.obstacle_dist_thresh_m = 1.5f;
        fsm->config.max_tilt_angle_rad = 0.436f;
        fsm->config.min_soc_for_retry = 0.22f;
        fsm->config.min_cell_voltage_v = 3.35f;
        fsm->config.cell_count = 6U;
        fsm->config.max_attempts = DEFAULT_MAX_ATTEMPTS;
        fsm->config.loiter_duration_ms = 15000U;
    }

    fsm->state = GA_STATE_APPROACH_DESCENT;
    fsm->attempt_counter = 0U;
    fsm->lidar_obstacle_counter = 0U;
    fsm->state_timer_ms = 0U;

    fsm->setpoints.target_alt_m = 0.0f;
    fsm->setpoints.target_vz_ms = -1.0f;
    fsm->setpoints.target_roll_rad = 0.0f;
    fsm->setpoints.target_pitch_rad = 0.0f;
    fsm->setpoints.max_tilt_limit_rad = 0.436f;
    fsm->setpoints.climb_priority = false;
    fsm->setpoints.emergency_land_now = false;
}

/* Перевірка тригерів аварійного скасування */
static bool check_abort_conditions(ga_fsm_t *fsm, const ga_telemetry_t *telem) {
    if (telem->operator_abort_req) {
        return true;
    }

    /* Фільтр антибрязкоту лідара */
    if (telem->lidar_valid && (telem->lidar_distance_m < fsm->config.obstacle_dist_thresh_m)) {
        if (fsm->lidar_obstacle_counter < LIDAR_CONFIRM_TICKS) {
            fsm->lidar_obstacle_counter++;
        }
    } else {
        fsm->lidar_obstacle_counter = 0U;
    }

    if (fsm->lidar_obstacle_counter >= LIDAR_CONFIRM_TICKS) {
        return true;
    }

    /* Критичне відхилення кутів орієнтації */
    if ((fabsf(telem->roll_rad) > fsm->config.max_tilt_angle_rad) ||
        (fabsf(telem->pitch_rad) > fsm->config.max_tilt_angle_rad)) {
        return true;
    }

    return false;
}

/* Перевірка енергетичного бюджету на повторне коло */
static bool check_energy_budget(const ga_fsm_t *fsm, const ga_telemetry_t *telem) {
    if (fsm->attempt_counter >= fsm->config.max_attempts) {
        return false;
    }

    if (telem->battery_soc < fsm->config.min_soc_for_retry) {
        return false;
    }

    float cell_v = telem->battery_voltage_v / (float)fsm->config.cell_count;
    if (cell_v < fsm->config.min_cell_voltage_v) {
        return false;
    }

    return true;
}

/* Головна функція такту автомата (50 Гц) */
void ga_fsm_step(ga_fsm_t *fsm, const ga_telemetry_t *telem, uint32_t now_ms) {
    switch (fsm->state) {
    case GA_STATE_APPROACH_DESCENT:
        fsm->setpoints.target_vz_ms = -1.0f;
        fsm->setpoints.climb_priority = false;
        fsm->setpoints.max_tilt_limit_rad = fsm->config.max_tilt_angle_rad;
        fsm->setpoints.emergency_land_now = false;

        if (check_abort_conditions(fsm, telem)) {
            float sinkage = calculate_sinkage(telem->vertical_speed_ms,
                                              fsm->config.max_thrust_to_weight,
                                              fsm->config.motor_spoolup_time_s);

            /* Якщо висота менша за просадку + запас, відхід неможливий -> екстрена посадка */
            if (telem->altitude_m < (sinkage + fsm->config.safety_margin_m)) {
                fsm->state = GA_STATE_EMERGENCY_FAILSAFE;
                fsm->setpoints.emergency_land_now = true;
            } else {
                fsm->attempt_counter++;
                fsm->state = GA_STATE_ABORT_BRAKE_CLIMB;
                fsm->setpoints.target_alt_m = telem->altitude_m + fsm->config.missed_approach_alt_m;
                fsm->state_timer_ms = now_ms;
            }
        }
        break;

    case GA_STATE_ABORT_BRAKE_CLIMB:
        /* Режим екстреного підйому: максимальний темп, нахили заблоковані */
        fsm->setpoints.target_vz_ms = 3.5f;
        fsm->setpoints.target_roll_rad = 0.0f;
        fsm->setpoints.target_pitch_rad = 0.0f;
        fsm->setpoints.max_tilt_limit_rad = 0.087f; /* Затиснуто до ~5 градусів */
        fsm->setpoints.climb_priority = true;

        if (telem->altitude_m >= fsm->setpoints.target_alt_m) {
            fsm->state = GA_STATE_ENERGY_AUDIT;
            fsm->state_timer_ms = now_ms;
        }
        break;

    case GA_STATE_ENERGY_AUDIT:
        fsm->setpoints.climb_priority = false;
        fsm->setpoints.target_vz_ms = 0.0f; /* Зависання для аналізу */
        fsm->setpoints.max_tilt_limit_rad = fsm->config.max_tilt_angle_rad;

        if (check_energy_budget(fsm, telem)) {
            fsm->state = GA_STATE_CIRCUIT_LOITER;
        } else {
            fsm->state = GA_STATE_EMERGENCY_FAILSAFE;
        }
        fsm->state_timer_ms = now_ms;
        break;

    case GA_STATE_CIRCUIT_LOITER:
        fsm->setpoints.target_vz_ms = 0.0f;
        /* Очікування завершення кола очікування перед повторним заходом */
        if ((now_ms - fsm->state_timer_ms) >= fsm->config.loiter_duration_ms) {
            fsm->state = GA_STATE_APPROACH_DESCENT;
            fsm->state_timer_ms = now_ms;
            fsm->lidar_obstacle_counter = 0U;
        }
        break;

    case GA_STATE_EMERGENCY_FAILSAFE:
        /* Аварійний спуск зі швидкістю 0.6 м/с або виконання Rally Divert */
        fsm->setpoints.target_vz_ms = -0.6f;
        fsm->setpoints.climb_priority = false;
        break;
    }
}
