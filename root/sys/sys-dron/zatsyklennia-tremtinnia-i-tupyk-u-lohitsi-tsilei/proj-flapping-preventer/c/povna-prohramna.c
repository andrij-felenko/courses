#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CYCLE_BUFFER_SIZE 16
#define MAX_NGRAM_LENGTH  4
#define RATE_BUFFER_SIZE  8

typedef enum {
    ESCALATION_NONE = 0,
    ESCALATION_STOCHASTIC_JITTER = 1,
    ESCALATION_VIRTUAL_OBSTACLE  = 2,
    ESCALATION_ALTITUDE_LAYER    = 3,
    ESCALATION_ABORT_LOITER      = 4
} escalation_level_t;

/* Блок гістерезисного компаратора */
typedef struct {
    float threshold_high; /* Поріг увімкнення */
    float threshold_low;  /* Поріг вимкнення */
    bool  current_state;  /* Поточний стан виходу */
} hysteresis_gate_t;

/* Блок таймерів Debounce та Dwell */
typedef struct {
    uint32_t debounce_time_us; /* Необхідний час підтвердження умови */
    uint32_t dwell_time_us;    /* Мінімальний час утримання стану */
    uint32_t condition_start_us;
    uint32_t state_entered_us;
    bool     pending_condition;
    bool     active_state;
} debounce_dwell_gate_t;

/* Запис просторово-часового підпису */
typedef struct {
    uint16_t state_id;
    int16_t  grid_x;
    int16_t  grid_y;
    int16_t  grid_z;
    uint32_t timestamp_ms;
} state_signature_t;

/* Детектор циклів дій */
typedef struct {
    state_signature_t history[CYCLE_BUFFER_SIZE];
    size_t  head_idx;
    size_t  count;
    float   grid_res_xy_m;
    float   grid_res_z_m;
    float   last_pos_x;
    float   last_pos_y;
    float   last_pos_z;
    uint8_t repeat_threshold;
} cycle_detector_t;

/* Статистичний аналізатор частоти перемикань */
typedef struct {
    uint32_t timestamps_us[RATE_BUFFER_SIZE];
    size_t   head_idx;
    size_t   count;
    float    current_rate_hz;
} rate_analyzer_t;

/* Повний контекст модуля запобігання аномаліям */
typedef struct {
    hysteresis_gate_t     hysteresis;
    debounce_dwell_gate_t gate;
    cycle_detector_t      detector;
    rate_analyzer_t       rate_stats;
    escalation_level_t    current_escalation;
    uint8_t               detected_cycle_len;
    uint16_t              suppressed_switch_count;
} flapping_preventer_t;

/* Ініціалізація гістерезису */
void hysteresis_init(hysteresis_gate_t *gate, float th_high, float th_low, bool initial) {
    gate->threshold_high = th_high;
    gate->threshold_low = th_low;
    gate->current_state = initial;
}

/* Оновлення гістерезису */
bool hysteresis_update(hysteresis_gate_t *gate, float value) {
    if (gate->current_state) {
        if (value <= gate->threshold_low) {
            gate->current_state = false;
        }
    } else {
        if (value >= gate->threshold_high) {
            gate->current_state = true;
        }
    }
    return gate->current_state;
}

/* Ініціалізація Debounce / Dwell логіки */
void debounce_dwell_init(debounce_dwell_gate_t *gate, uint32_t debounce_us, uint32_t dwell_us, uint32_t now_us) {
    gate->debounce_time_us = debounce_us;
    gate->dwell_time_us = dwell_us;
    gate->condition_start_us = 0;
    gate->state_entered_us = now_us;
    gate->pending_condition = false;
    gate->active_state = false;
}

/* Оновлення часового фільтра */
bool debounce_dwell_update(debounce_dwell_gate_t *gate, bool raw_condition, uint32_t now_us, bool emergency) {
    if (emergency) {
        gate->active_state = false;
        gate->pending_condition = false;
        gate->state_entered_us = now_us;
        return false;
    }

    if (gate->active_state) {
        if (!raw_condition) {
            uint32_t time_in_state = now_us - gate->state_entered_us;
            if (time_in_state >= gate->dwell_time_us) {
                gate->active_state = false;
                gate->state_entered_us = now_us;
                gate->pending_condition = false;
            }
        } else {
            gate->pending_condition = false;
        }
    } else {
        if (raw_condition) {
            if (!gate->pending_condition) {
                gate->pending_condition = true;
                gate->condition_start_us = now_us;
            } else {
                uint32_t duration = now_us - gate->condition_start_us;
                if (duration >= gate->debounce_time_us) {
                    gate->active_state = true;
                    gate->state_entered_us = now_us;
                    gate->pending_condition = false;
                }
            }
        } else {
            gate->pending_condition = false;
        }
    }
    return gate->active_state;
}

/* Ініціалізація аналізатора частоти */
void rate_analyzer_init(rate_analyzer_t *rate) {
    rate->head_idx = 0;
    rate->count = 0;
    rate->current_rate_hz = 0.0f;
}

/* Реєстрація події перемикання */
void rate_analyzer_record_event(rate_analyzer_t *rate, uint32_t now_us) {
    rate->timestamps_us[rate->head_idx] = now_us;
    rate->head_idx = (rate->head_idx + 1) % RATE_BUFFER_SIZE;
    if (rate->count < RATE_BUFFER_SIZE) {
        rate->count++;
    }
    if (rate->count >= 2) {
        size_t oldest_idx = (rate->head_idx + RATE_BUFFER_SIZE - rate->count) % RATE_BUFFER_SIZE;
        uint32_t dt_us = now_us - rate->timestamps_us[oldest_idx];
        if (dt_us > 0) {
            rate->current_rate_hz = ((float)(rate->count - 1) * 1000000.0f) / (float)dt_us;
        }
    }
}

/* Ініціалізація детектора циклів */
void cycle_detector_init(cycle_detector_t *det, float res_xy, float res_z, uint8_t rep_th) {
    det->head_idx = 0;
    det->count = 0;
    det->grid_res_xy_m = (res_xy > 0.1f) ? res_xy : 5.0f;
    det->grid_res_z_m = (res_z > 0.1f) ? res_z : 2.0f;
    det->repeat_threshold = rep_th;
    det->last_pos_x = -1e9f;
    det->last_pos_y = -1e9f;
    det->last_pos_z = -1e9f;
}

/* Перевірка ідентичності двох підписів */
static inline bool signatures_equal(const state_signature_t *a, const state_signature_t *b) {
    return (a->state_id == b->state_id) &&
           (a->grid_x == b->grid_x) &&
           (a->grid_y == b->grid_y) &&
           (a->grid_z == b->grid_z);
}

/* Отримання підпису з буфера за зсувом від найновішого */
static inline const state_signature_t* get_signature_offset(const cycle_detector_t *det, size_t offset) {
    size_t idx = (det->head_idx + CYCLE_BUFFER_SIZE - 1 - offset) % CYCLE_BUFFER_SIZE;
    return &det->history[idx];
}

/* Оновлення детектора циклів */
uint8_t cycle_detector_push(cycle_detector_t *det, uint16_t state_id, float x, float y, float z, uint32_t now_ms) {
    int16_t gx = (int16_t)(x / det->grid_res_xy_m);
    int16_t gy = (int16_t)(y / det->grid_res_xy_m);
    int16_t gz = (int16_t)(z / det->grid_res_z_m);

    /* Фільтрація брязкоту на границі вокселя */
    if (det->count > 0) {
        const state_signature_t *last = get_signature_offset(det, 0);
        if (last->state_id == state_id && last->grid_x == gx && last->grid_y == gy && last->grid_z == gz) {
            return 0; /* Немає істотної зміни */
        }
        float dx = x - det->last_pos_x;
        float dy = y - det->last_pos_y;
        float dz = z - det->last_pos_z;
        float dist_sq = dx*dx + dy*dy;
        float min_dist_sq = 0.25f * det->grid_res_xy_m * det->grid_res_xy_m;
        if (last->state_id == state_id && dist_sq < min_dist_sq && (dz * dz < 0.25f * det->grid_res_z_m * det->grid_res_z_m)) {
            return 0;
        }
    }

    /* Запис нового підпису */
    det->history[det->head_idx].state_id = state_id;
    det->history[det->head_idx].grid_x = gx;
    det->history[det->head_idx].grid_y = gy;
    det->history[det->head_idx].grid_z = gz;
    det->history[det->head_idx].timestamp_ms = now_ms;

    det->head_idx = (det->head_idx + 1) % CYCLE_BUFFER_SIZE;
    if (det->count < CYCLE_BUFFER_SIZE) {
        det->count++;
    }
    det->last_pos_x = x;
    det->last_pos_y = y;
    det->last_pos_z = z;

    /* N-грамний пошук повторюваних циклів */
    for (uint8_t len = 2; len <= MAX_NGRAM_LENGTH; ++len) {
        size_t needed_count = (size_t)len * det->repeat_threshold;
        if (det->count < needed_count) {
            continue;
        }

        bool match = true;
        for (uint8_t rep = 1; rep < det->repeat_threshold; ++rep) {
            for (uint8_t i = 0; i < len; ++i) {
                const state_signature_t *sig_curr = get_signature_offset(det, i);
                const state_signature_t *sig_prev = get_signature_offset(det, (size_t)rep * len + i);
                if (!signatures_equal(sig_curr, sig_prev)) {
                    match = false;
                    break;
                }
            }
            if (!match) break;
        }

        if (match) {
            return len; /* Знайдено цикл вказаної довжини */
        }
    }
    return 0;
}

/* Ініціалізація повного модуля */
void flapping_preventer_init(flapping_preventer_t *fp,
                             float th_high, float th_low,
                             uint32_t debounce_us, uint32_t dwell_us,
                             float grid_xy, float grid_z,
                             uint32_t now_us)
{
    hysteresis_init(&fp->hysteresis, th_high, th_low, false);
    debounce_dwell_init(&fp->gate, debounce_us, dwell_us, now_us);
    cycle_detector_init(&fp->detector, grid_xy, grid_z, 3);
    rate_analyzer_init(&fp->rate_stats);
    fp->current_escalation = ESCALATION_NONE;
    fp->detected_cycle_len = 0;
    fp->suppressed_switch_count = 0;
}

/* Головна функція обробки кроку */
bool flapping_preventer_process(flapping_preventer_t *fp,
                               float metric_val,
                               uint16_t current_state_id,
                               float x, float y, float z,
                               uint32_t now_us,
                               bool emergency)
{
    bool raw = hysteresis_update(&fp->hysteresis, metric_val);
    bool prev_active = fp->gate.active_state;
    bool active = debounce_dwell_update(&fp->gate, raw, now_us, emergency);

    if (raw != active) {
        fp->suppressed_switch_count++;
    }

    if (active != prev_active) {
        rate_analyzer_record_event(&fp->rate_stats, now_us);
    }

    uint8_t cycle = cycle_detector_push(&fp->detector, current_state_id, x, y, z, now_us / 1000);
    if (cycle > 0) {
        fp->detected_cycle_len = cycle;
        if (fp->current_escalation < ESCALATION_ABORT_LOITER) {
            fp->current_escalation = (escalation_level_t)((int)fp->current_escalation + 1);
        }
    }

    return active;
}
