#include <stdint.h>
#include <stdbool.h>

#define HYST_MEDIAN_SIZE 5

typedef enum {
    HYST_HEATING = 0, /* УВІМК при T <= T_low, ВИМК при T >= T_high */
    HYST_COOLING = 1  /* УВІМК при T >= T_high, ВИМК при T <= T_low */
} hyst_type_t;

typedef struct {
    float threshold_low;
    float threshold_high;
    uint32_t min_on_ms;
    uint32_t min_off_ms;
    float ema_alpha;
    hyst_type_t type;
} hyst_params_t;

typedef struct {
    float ring_buf[HYST_MEDIAN_SIZE];
    uint8_t ring_head;
    uint8_t count;
    float ema_filtered;
    bool is_initialized;
    bool output_state;
    uint32_t last_transition_ms;
} hyst_fsm_t;

static float get_median_5(float *src, uint8_t n) {
    float sorted[HYST_MEDIAN_SIZE];
    for (uint8_t i = 0; i < n; i++) sorted[i] = src[i];
    
    /* Сортування вставками для n <= 5 */
    for (uint8_t i = 1; i < n; i++) {
        float key = sorted[i];
        int8_t j = (int8_t)i - 1;
        while (j >= 0 && sorted[j] > key) {
            sorted[j + 1] = sorted[j];
            j--;
        }
        sorted[j + 1] = key;
    }
    return sorted[n / 2];
}

void hyst_fsm_init(hyst_fsm_t *fsm, uint32_t now_ms) {
    fsm->ring_head = 0;
    fsm->count = 0;
    fsm->ema_filtered = 0.0f;
    fsm->is_initialized = false;
    fsm->output_state = false;
    fsm->last_transition_ms = now_ms;
}

bool hyst_fsm_process(hyst_fsm_t *fsm, const hyst_params_t *params, float raw_val, uint32_t now_ms) {
    /* 1. Медіанний фільтр */
    fsm->ring_buf[fsm->ring_head] = raw_val;
    fsm->ring_head = (fsm->ring_head + 1) % HYST_MEDIAN_SIZE;
    if (fsm->count < HYST_MEDIAN_SIZE) fsm->count++;
    float med = get_median_5(fsm->ring_buf, fsm->count);

    /* 2. Експоненційне згладжування EMA */
    if (!fsm->is_initialized) {
        fsm->ema_filtered = med;
        fsm->is_initialized = true;
    } else {
        fsm->ema_filtered = params->ema_alpha * med + (1.0f - params->ema_alpha) * fsm->ema_filtered;
    }

    /* 3. Перевірка часового блокування (Hold-off) */
    uint32_t dt = now_ms - fsm->last_transition_ms;
    uint32_t required_hold = fsm->output_state ? params->min_on_ms : params->min_off_ms;
    if (dt < required_hold) {
        return fsm->output_state; /* Зміна стану заблокована таймером */
    }

    /* 4. Компаратор Шмітта з амплітудною петлею */
    bool target_state = fsm->output_state;
    if (params->type == HYST_HEATING) {
        if (fsm->ema_filtered <= params->threshold_low) {
            target_state = true;
        } else if (fsm->ema_filtered >= params->threshold_high) {
            target_state = false;
        }
    } else {
        if (fsm->ema_filtered >= params->threshold_high) {
            target_state = true;
        } else if (fsm->ema_filtered <= params->threshold_low) {
            target_state = false;
        }
    }

    if (target_state != fsm->output_state) {
        fsm->output_state = target_state;
        fsm->last_transition_ms = now_ms;
    }

    return fsm->output_state;
}
