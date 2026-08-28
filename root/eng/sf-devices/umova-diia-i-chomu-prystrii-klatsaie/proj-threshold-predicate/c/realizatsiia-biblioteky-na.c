#include <stdint.h>
#include <stdbool.h>

/* ========================================================================= */
/* 1. Цілочисельний компаратор (для сирих кодів АЦП / фіксованої крапки)      */
/* ========================================================================= */

typedef struct {
    int32_t low_threshold;   /* Поріг вимкнення: перехід 1 -> 0 */
    int32_t high_threshold;  /* Поріг увімкнення: перехід 0 -> 1 */
} hysteresis_cfg_i32_t;

typedef struct {
    bool current_state;      /* Поточний логічний вихід (true = 1, false = 0) */
    bool initialized;        /* Чи було виконано ініціалізацію стартового стану */
} hysteresis_state_i32_t;

/**
 * @brief Ініціалізація меж за номінальною уставкою та симетричною мертвою зоною
 */
static inline bool hysteresis_cfg_init_symmetric_i32(hysteresis_cfg_i32_t *cfg,
                                                     int32_t setpoint,
                                                     int32_t deadband) {
    if (!cfg || deadband <= 0) {
        return false;
    }
    int32_t half = deadband / 2;
    cfg->low_threshold = setpoint - half;
    cfg->high_threshold = setpoint + (deadband - half);
    return true;
}

/**
 * @brief Крок оновлення стану цілочисельного компаратора
 */
static inline bool hysteresis_update_i32(const hysteresis_cfg_i32_t *cfg,
                                        hysteresis_state_i32_t *state,
                                        int32_t raw_sample) {
    if (!state->initialized) {
        /* Стратегія холодного старту: активний рівень 1 лише якщо значення строго
         * досягло або перевищило верхню межу. В усіх інших випадках — безпечний 0 */
        state->current_state = (raw_sample >= cfg->high_threshold);
        state->initialized = true;
        return state->current_state;
    }

    if (state->current_state) {
        /* Стан 1 (активний): перехід у 0 лише при спаді нижче low_threshold */
        if (raw_sample <= cfg->low_threshold) {
            state->current_state = false;
        }
    } else {
        /* Стан 0 (неактивний): перехід в 1 лише при підйомі вище high_threshold */
        if (raw_sample >= cfg->high_threshold) {
            state->current_state = true;
        }
    }

    return state->current_state;
}

/* ========================================================================= */
/* 2. Компаратор чисел із рухомою комою (float)                               */
/* ========================================================================= */

typedef struct {
    float low_threshold;
    float high_threshold;
} hysteresis_cfg_f32_t;

typedef struct {
    bool current_state;
    bool initialized;
} hysteresis_state_f32_t;

static inline bool hysteresis_cfg_init_symmetric_f32(hysteresis_cfg_f32_t *cfg,
                                                     float setpoint,
                                                     float deadband) {
    if (!cfg || deadband <= 0.0f) {
        return false;
    }
    float half = deadband * 0.5f;
    cfg->low_threshold = setpoint - half;
    cfg->high_threshold = setpoint + half;
    return true;
}

static inline bool hysteresis_update_f32(const hysteresis_cfg_f32_t *cfg,
                                        hysteresis_state_f32_t *state,
                                        float sample) {
    if (!state->initialized) {
        state->current_state = (sample >= cfg->high_threshold);
        state->initialized = true;
        return state->current_state;
    }

    if (state->current_state) {
        if (sample <= cfg->low_threshold) {
            state->current_state = false;
        }
    } else {
        if (sample >= cfg->high_threshold) {
            state->current_state = true;
        }
    }

    return state->current_state;
}
