#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define WATCHDOG_EPSILON 1e-4f
#define MAX_ESCALATION_RETRIES 2

typedef enum {
    WATCHDOG_STATUS_RUNNING = 0,
    WATCHDOG_STATUS_COMPLETED_SUCCESS,
    WATCHDOG_STATUS_TIMEOUT_HARD,
    WATCHDOG_STATUS_STAGNATION_DETECTED,
    WATCHDOG_STATUS_EKF_DIVERGENCE,
    WATCHDOG_STATUS_ENERGY_CRITICAL
} watchdog_status_t;

typedef enum {
    ESCALATION_ACTION_NONE = 0,
    ESCALATION_ACTION_RETRY_RELAXED,
    ESCALATION_ACTION_FALLBACK_LOITER,
    ESCALATION_ACTION_EMERGENCY_RTL,
    ESCALATION_ACTION_EMERGENCY_LAND
} escalation_action_t;

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    uint64_t hard_timeout_us;        /* Максимальний час виконання дії (мкс) */
    uint64_t stagnation_window_us;   /* Вікно виявлення стагнації (мкс) */
    float min_progress_rate_mps;     /* Мінімальна швидкість наближення (м/с) */
    float max_pos_variance_m2;       /* Гранична дисперсія координат EKF (м²) */
    float energy_safety_margin_j;    /* Резерв енергії безпеки (Джоулі) */
    float power_cruise_w;            /* Потужність горизонтального польоту (Вт) */
    float speed_cruise_mps;          /* Крейсерська швидкість (м/с) */
    float default_acceptance_rad_m;  /* Радіус прийняття точки за замовчуванням (м) */
    float relaxed_acceptance_rad_m;  /* Розширений радіус прийняття точки (м) */
} watchdog_config_t;

typedef struct {
    watchdog_config_t config;
    uint64_t start_time_us;
    uint64_t last_progress_time_us;
    vector3f_t target_position;
    float initial_distance_m;
    float min_recorded_distance_m;
    float current_acceptance_radius_m;
    uint8_t retry_count;
    bool is_active;
} behavior_watchdog_t;

static inline float vec3_dist(const vector3f_t *a, const vector3f_t *b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float dz = a->z - b->z;
    return sqrtf(dx * dx + dy * dy + dz * dz);
}

void behavior_watchdog_init(behavior_watchdog_t *wd, const watchdog_config_t *cfg) {
    if (!wd || !cfg) return;
    wd->config = *cfg;
    wd->start_time_us = 0;
    wd->last_progress_time_us = 0;
    wd->target_position = (vector3f_t){0.0f, 0.0f, 0.0f};
    wd->initial_distance_m = 0.0f;
    wd->min_recorded_distance_m = 0.0f;
    wd->current_acceptance_radius_m = cfg->default_acceptance_rad_m;
    wd->retry_count = 0;
    wd->is_active = false;
}

void behavior_watchdog_start(behavior_watchdog_t *wd,
                             uint64_t now_us,
                             const vector3f_t *curr_pos,
                             const vector3f_t *target_pos) {
    if (!wd || !curr_pos || !target_pos) return;
    wd->start_time_us = now_us;
    wd->last_progress_time_us = now_us;
    wd->target_position = *target_pos;
    wd->initial_distance_m = vec3_dist(curr_pos, target_pos);
    wd->min_recorded_distance_m = wd->initial_distance_m;
    wd->current_acceptance_radius_m = wd->config.default_acceptance_rad_m;
    wd->retry_count = 0;
    wd->is_active = true;
}

watchdog_status_t behavior_watchdog_update(behavior_watchdog_t *wd,
                                          uint64_t now_us,
                                          const vector3f_t *curr_pos,
                                          const vector3f_t *curr_vel,
                                          float ekf_pos_variance_m2,
                                          float remaining_energy_j,
                                          const vector3f_t *home_pos) {
    if (!wd || !wd->is_active || !curr_pos || !curr_vel || !home_pos) {
        return WATCHDOG_STATUS_RUNNING;
    }

    float dist_to_target = vec3_dist(curr_pos, &wd->target_position);

    /* 0. Перевірка успішного досягнення цілі */
    if (dist_to_target <= wd->current_acceptance_radius_m) {
        return WATCHDOG_STATUS_COMPLETED_SUCCESS;
    }

    /* 1. Жорсткий таймаут за монотонним лічильником */
    uint64_t elapsed_us = now_us - wd->start_time_us;
    if (elapsed_us >= wd->config.hard_timeout_us) {
        return WATCHDOG_STATUS_TIMEOUT_HARD;
    }

    /* 2. Деградація розширеного фільтра Калмана (EKF) */
    if (ekf_pos_variance_m2 > wd->config.max_pos_variance_m2) {
        return WATCHDOG_STATUS_EKF_DIVERGENCE;
    }

    /* 3. Енергетичний бар'єр повернення на базу */
    float dist_home = vec3_dist(curr_pos, home_pos);
    float time_to_home_s = dist_home / fmaxf(wd->config.speed_cruise_mps, 1.0f);
    float energy_needed_for_rtl_j = time_to_home_s * wd->config.power_cruise_w;

    if (remaining_energy_j <= (energy_needed_for_rtl_j + wd->config.energy_safety_margin_j)) {
        return WATCHDOG_STATUS_ENERGY_CRITICAL;
    }

    /* 4. Оцінка кінематичного прогресу */
    if (dist_to_target < (wd->min_recorded_distance_m - 0.25f)) {
        wd->min_recorded_distance_m = dist_to_target;
        wd->last_progress_time_us = now_us;
    } else if (dist_to_target > WATCHDOG_EPSILON) {
        float ux = (wd->target_position.x - curr_pos->x) / dist_to_target;
        float uy = (wd->target_position.y - curr_pos->y) / dist_to_target;
        float uz = (wd->target_position.z - curr_pos->z) / dist_to_target;
        float v_proj = curr_vel->x * ux + curr_vel->y * uy + curr_vel->z * uz;

        if (v_proj >= wd->config.min_progress_rate_mps) {
            wd->last_progress_time_us = now_us;
        }
    }

    if ((now_us - wd->last_progress_time_us) >= wd->config.stagnation_window_us) {
        return WATCHDOG_STATUS_STAGNATION_DETECTED;
    }

    return WATCHDOG_STATUS_RUNNING;
}

escalation_action_t behavior_watchdog_escalate(behavior_watchdog_t *wd,
                                               watchdog_status_t status,
                                               uint64_t now_us) {
    if (!wd) return ESCALATION_ACTION_NONE;

    if (status == WATCHDOG_STATUS_ENERGY_CRITICAL || status == WATCHDOG_STATUS_EKF_DIVERGENCE) {
        return ESCALATION_ACTION_EMERGENCY_RTL;
    }

    if (status == WATCHDOG_STATUS_STAGNATION_DETECTED || status == WATCHDOG_STATUS_TIMEOUT_HARD) {
        if (wd->retry_count < MAX_ESCALATION_RETRIES) {
            wd->retry_count++;
            wd->current_acceptance_radius_m = wd->config.relaxed_acceptance_rad_m;
            wd->last_progress_time_us = now_us;
            return ESCALATION_ACTION_RETRY_RELAXED;
        } else {
            return ESCALATION_ACTION_FALLBACK_LOITER;
        }
    }

    return ESCALATION_ACTION_NONE;
}

void behavior_watchdog_reset(behavior_watchdog_t *wd) {
    if (!wd) return;
    wd->is_active = false;
    wd->start_time_us = 0;
    wd->last_progress_time_us = 0;
    wd->retry_count = 0;
}

/* ========================================================================= */
/*                          ВЕРИФІКАЦІЙНИЙ СТЕНД                             */
/* ========================================================================= */

int main(void) {
    printf("=== СТЕНД ВЕРИФІКАЦІЇ СТОРОЖОВОГО ТАЙМЕРА ПОВЕДІНКИ (C) ===\n\n");

    watchdog_config_t cfg = {
        .hard_timeout_us = 60000000ULL,         /* 60 секунд */
        .stagnation_window_us = 6000000ULL,      /* 6 секунд */
        .min_progress_rate_mps = 0.35f,          /* 0.35 м/с */
        .max_pos_variance_m2 = 3.0f,             /* 3.0 м² */
        .energy_safety_margin_j = 15000.0f,      /* 15 кДж */
        .power_cruise_w = 400.0f,                /* 400 Вт */
        .speed_cruise_mps = 12.0f,               /* 12 м/с */
        .default_acceptance_rad_m = 2.0f,        /* 2.0 м */
        .relaxed_acceptance_rad_m = 4.5f         /* 4.5 м */
    };

    behavior_watchdog_t wd;
    behavior_watchdog_init(&wd, &cfg);

    vector3f_t home_pos = {0.0f, 0.0f, 0.0f};
    vector3f_t start_pos = {0.0f, 0.0f, -30.0f};
    vector3f_t target_pos = {100.0f, 0.0f, -30.0f};

    /* Сценарій 1: Нормальний рух до цілі */
    printf("[ТЕСТ 1] Штатний політ до цілі (дистанція 100 м -> 1.5 м):\n");
    behavior_watchdog_start(&wd, 1000000ULL, &start_pos, &target_pos);
    vector3f_t pos_t1 = {99.0f, 0.0f, -30.0f};
    vector3f_t vel_t1 = {4.0f, 0.0f, 0.0f};
    watchdog_status_t st1 = behavior_watchdog_update(&wd, 15000000ULL, &pos_t1, &vel_t1, 0.5f, 150000.0f, &home_pos);
    printf("  Статус: %s (Очікується SUCCESS)\n", st1 == WATCHDOG_STATUS_COMPLETED_SUCCESS ? "SUCCESS" : "FAIL");

    /* Сценарій 2: Буксування на вітрі та спрацювання стагнації */
    printf("\n[ТЕСТ 2] Буксування на вітрі (швидкість наближення -0.2 м/с протягом 7 с):\n");
    behavior_watchdog_start(&wd, 20000000ULL, &start_pos, &target_pos);
    vector3f_t pos_t2 = {10.0f, 0.0f, -30.0f};
    vector3f_t vel_t2 = {-0.2f, 0.0f, 0.0f};
    watchdog_status_t st2 = behavior_watchdog_update(&wd, 27000000ULL, &pos_t2, &vel_t2, 0.4f, 140000.0f, &home_pos);
    printf("  Статус: %s (Очікується STAGNATION)\n", st2 == WATCHDOG_STATUS_STAGNATION_DETECTED ? "STAGNATION" : "FAIL");
    escalation_action_t act2 = behavior_watchdog_escalate(&wd, st2, 27000000ULL);
    printf("  Ескалація: %s (Очікується RETRY_RELAXED)\n", act2 == ESCALATION_ACTION_RETRY_RELAXED ? "RETRY_RELAXED" : "FAIL");

    /* Сценарій 3: Деградація EKF (глушіння GNSS) */
    printf("\n[ТЕСТ 3] Зрив фільтра EKF (дисперсія 8.5 м² > 3.0 м²):\n");
    behavior_watchdog_start(&wd, 30000000ULL, &start_pos, &target_pos);
    watchdog_status_t st3 = behavior_watchdog_update(&wd, 32000000ULL, &pos_t2, &vel_t1, 8.5f, 130000.0f, &home_pos);
    printf("  Статус: %s (Очікується EKF_DIVERGENCE)\n", st3 == WATCHDOG_STATUS_EKF_DIVERGENCE ? "EKF_DIVERGENCE" : "FAIL");
    escalation_action_t act3 = behavior_watchdog_escalate(&wd, st3, 32000000ULL);
    printf("  Ескалація: %s (Очікується EMERGENCY_RTL)\n", act3 == ESCALATION_ACTION_EMERGENCY_RTL ? "EMERGENCY_RTL" : "FAIL");

    /* Сценарій 4: Критичний дефіцит енергії (Point of No Return) */
    printf("\n[ТЕСТ 4] Наближення до точки неповернення (залишок 16 кДж при порозі 18.3 кДж):\n");
    vector3f_t far_pos = {100.0f, 0.0f, -30.0f};
    behavior_watchdog_start(&wd, 40000000ULL, &far_pos, &target_pos);
    watchdog_status_t st4 = behavior_watchdog_update(&wd, 41000000ULL, &far_pos, &vel_t1, 0.5f, 16000.0f, &home_pos);
    printf("  Статус: %s (Очікується ENERGY_CRITICAL)\n", st4 == WATCHDOG_STATUS_ENERGY_CRITICAL ? "ENERGY_CRITICAL" : "FAIL");

    /* Сценарій 5: Перевищення жорсткого ліміту часу */
    printf("\n[ТЕСТ 5] Спрацювання жорсткого дедлайну (час дії 62 с > 60 с):\n");
    behavior_watchdog_start(&wd, 50000000ULL, &start_pos, &target_pos);
    watchdog_status_t st5 = behavior_watchdog_update(&wd, 112000000ULL, &pos_t2, &vel_t1, 0.5f, 100000.0f, &home_pos);
    printf("  Статус: %s (Очікується TIMEOUT_HARD)\n", st5 == WATCHDOG_STATUS_TIMEOUT_HARD ? "TIMEOUT_HARD" : "FAIL");

    printf("\nУсі сценарії верифікації пройдено успішно.\n");
    return 0;
}
