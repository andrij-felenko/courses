#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define WATCHDOG_EPSILON 1e-4f

typedef enum {
    EVAL_RESULT_OK = 0,
    EVAL_RESULT_HARD_TIMEOUT,
    EVAL_RESULT_STAGNATION,
    EVAL_RESULT_EKF_DIVERGENCE,
    EVAL_RESULT_ENERGY_CRITICAL
} behavior_eval_result_t;

typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

typedef struct {
    uint64_t hard_limit_us;       /* Жорсткий граничний дедлайн (мкс) */
    uint64_t stagnation_time_us;  /* Вікно фіксації відсутності наближення (мкс) */
    float min_speed_mps;          /* Поріг швидкості наближення (м/с) */
    float max_pos_variance_m2;    /* Гранична дисперсія координат EKF (м²) */
    float cruise_power_w;         /* Крейсерська потужність польоту (Вт) */
    float cruise_speed_mps;       /* Крейсерська швидкість руху (м/с) */
    float energy_margin_j;        /* Незнижуваний резерв енергії для RTL (Дж) */
} behavior_params_t;

typedef struct {
    uint64_t start_time_us;
    uint64_t last_progress_us;
    vec3_t target_pos;
    float min_distance_recorded_m;
    uint8_t retry_count;
    bool is_active;
} behavior_state_t;

static inline float vec3_dist(const vec3_t *a, const vec3_t *b) {
    float dx = a->x - b->x;
    float dy = a->y - b->y;
    float dz = a->z - b->z;
    return sqrtf(dx * dx + dy * dy + dz * dz);
}

/* Оцінка інваріантів поточної поведінки в реальному часі */
behavior_eval_result_t evaluate_behavior_safety(const behavior_params_t *params,
                                               behavior_state_t *state,
                                               uint64_t now_us,
                                               const vec3_t *curr_pos,
                                               const vec3_t *curr_vel,
                                               float ekf_variance_m2,
                                               float remaining_energy_j,
                                               const vec3_t *home_pos) {
    if (!state->is_active) {
        return EVAL_RESULT_OK;
    }

    /* 1. Перевірка жорсткого таймауту за монотонним лічильником */
    if ((now_us - state->start_time_us) >= params->hard_limit_us) {
        return EVAL_RESULT_HARD_TIMEOUT;
    }

    /* 2. Перевірка розбіжності та деградації оцінки фільтра EKF */
    if (ekf_variance_m2 > params->max_pos_variance_m2) {
        return EVAL_RESULT_EKF_DIVERGENCE;
    }

    /* 3. Оцінка енергетичного бюджету повернення додому */
    float dist_home = vec3_dist(curr_pos, home_pos);
    float time_to_home_s = dist_home / fmaxf(params->cruise_speed_mps, 1.0f);
    float energy_needed_for_rtl_j = time_to_home_s * params->cruise_power_w;

    if (remaining_energy_j <= (energy_needed_for_rtl_j + params->energy_margin_j)) {
        return EVAL_RESULT_ENERGY_CRITICAL;
    }

    /* 4. Оцінка просторового наближення до цільової точки */
    float current_dist = vec3_dist(curr_pos, &state->target_pos);

    if (current_dist < (state->min_distance_recorded_m - 0.25f)) {
        state->min_distance_recorded_m = current_dist;
        state->last_progress_us = now_us;
    } else if (current_dist > WATCHDOG_EPSILON) {
        /* Обчислення проекції швидкості на одиничний вектор напрямку */
        float ux = (state->target_pos.x - curr_pos->x) / current_dist;
        float uy = (state->target_pos.y - curr_pos->y) / current_dist;
        float uz = (state->target_pos.z - curr_pos->z) / current_dist;
        float v_proj = curr_vel->x * ux + curr_vel->y * uy + curr_vel->z * uz;

        if (v_proj >= params->min_speed_mps) {
            state->last_progress_us = now_us;
        }
    }

    /* Перевірка тривалості стагнації */
    if ((now_us - state->last_progress_us) >= params->stagnation_time_us) {
        return EVAL_RESULT_STAGNATION;
    }

    return EVAL_RESULT_OK;
}
