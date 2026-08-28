#include "hysteresis_controller.h"

static float calculate_median5(float *buf, uint8_t count) {
    float temp[HYST_MEDIAN_WINDOW];
    for (uint8_t i = 0; i < count; ++i) {
        temp[i] = buf[i];
    }
    /* Сортування вставками для 3..5 елементів найшвидше на мікроконтролерах */
    for (uint8_t i = 1; i < count; ++i) {
        float key = temp[i];
        int32_t j = (int32_t)i - 1;
        while (j >= 0 && temp[j] > key) {
            temp[j + 1] = temp[j];
            j--;
        }
        temp[j + 1] = key;
    }
    return temp[count / 2];
}

void hyst_init(hyst_controller_t *ctrl, const hyst_config_t *cfg, uint32_t now_ms) {
    if (!ctrl || !cfg) return;
    ctrl->cfg = *cfg;
    ctrl->state.median_idx = 0;
    ctrl->state.median_count = 0;
    ctrl->state.ema_val = 0.0f;
    ctrl->state.ema_initialized = false;
    ctrl->state.current_state = false;
    ctrl->state.last_switch_ms = now_ms;
}

bool hyst_update(hyst_controller_t *ctrl, float raw_sample, uint32_t now_ms) {
    if (!ctrl) return false;
    hyst_state_t *st = &ctrl->state;
    const hyst_config_t *cfg = &ctrl->cfg;

    /* 1. Запис у кільцевий буфер та обчислення медіани */
    st->median_buf[st->median_idx] = raw_sample;
    st->median_idx = (st->median_idx + 1) % HYST_MEDIAN_WINDOW;
    if (st->median_count < HYST_MEDIAN_WINDOW) {
        st->median_count++;
    }
    float median_val = calculate_median5(st->median_buf, st->median_count);

    /* 2. Експоненційне згладжування EMA */
    if (!st->ema_initialized) {
        st->ema_val = median_val;
        st->ema_initialized = true;
    } else {
        st->ema_val = cfg->ema_alpha * median_val + (1.0f - cfg->ema_alpha) * st->ema_val;
    }

    /* 3. Часове блокування (безпечне віднімання uint32_t при переповненні) */
    uint32_t elapsed_ms = now_ms - st->last_switch_ms;
    uint32_t required_hold = st->current_state ? cfg->min_on_time_ms : cfg->min_off_time_ms;

    if (elapsed_ms < required_hold) {
        return st->current_state;
    }

    /* 4. Компаратор Шмітта */
    bool desired_state = st->current_state;
    if (cfg->mode == HYST_MODE_ACTIVE_LOW) {
        if (st->ema_val <= cfg->threshold_low) {
            desired_state = true;
        } else if (st->ema_val >= cfg->threshold_high) {
            desired_state = false;
        }
    } else {
        if (st->ema_val >= cfg->threshold_high) {
            desired_state = true;
        } else if (st->ema_val <= cfg->threshold_low) {
            desired_state = false;
        }
    }

    if (desired_state != st->current_state) {
        st->current_state = desired_state;
        st->last_switch_ms = now_ms;
    }

    return st->current_state;
}

bool hyst_get_state(const hyst_controller_t *ctrl) {
    return ctrl ? ctrl->state.current_state : false;
}

float hyst_get_filtered_value(const hyst_controller_t *ctrl) {
    return ctrl ? ctrl->state.ema_val : 0.0f;
}
