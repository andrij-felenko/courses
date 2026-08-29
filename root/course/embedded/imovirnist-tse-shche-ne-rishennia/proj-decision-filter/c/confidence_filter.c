#include "confidence_filter.h"

#include <math.h>

/* Підрахунок одиниць у слові. На Cortex-M компілятор розгортає __builtin_popcount
 * у кілька інструкцій без циклу; запасний варіант — класичний SWAR, теж без циклу,
 * бо цикл у перериванні дав би розкид часу виконання. */
static inline unsigned popcount32(uint32_t v) {
#if defined(__GNUC__) || defined(__clang__)
    return (unsigned)__builtin_popcount(v);
#else
    v = v - ((v >> 1) & 0x55555555U);
    v = (v & 0x33333333U) + ((v >> 2) & 0x33333333U);
    v = (v + (v >> 4)) & 0x0F0F0F0FU;
    return (unsigned)((v * 0x01010101U) >> 24);
#endif
}

/* Маска дійсних бітів вікна. Зсув 1U << 32 — невизначена поведінка,
 * тому повна ширина обробляється окремою гілкою. */
static inline uint32_t window_mask(uint8_t window_size) {
    return (window_size >= (uint8_t)CONFIDENCE_WINDOW_MAX)
               ? 0xFFFFFFFFU
               : ((1U << window_size) - 1U);
}

bool confidence_config_valid(const ConfidenceFilterConfig *cfg) {
    if (cfg == NULL) {
        return false;
    }
    if (!(cfg->temperature > 0.0f) || !isfinite(cfg->temperature)) {
        return false;
    }
    if (!(cfg->alpha > 0.0f) || !(cfg->alpha < 1.0f)) {
        return false;
    }
    if (!(cfg->thresh_off >= 0.0f) || !(cfg->thresh_on <= 1.0f)) {
        return false;
    }
    /* Зворотний гістерезис (H_off вище за H_on) перетворив би автомат на
     * генератор брязкоту — саме на те, від чого фільтр і рятує. */
    if (cfg->thresh_off > cfg->thresh_on) {
        return false;
    }
    if (cfg->window_size == 0U || cfg->window_size > (uint8_t)CONFIDENCE_WINDOW_MAX) {
        return false;
    }
    if (cfg->min_votes == 0U || cfg->min_votes > cfg->window_size) {
        return false;
    }
    return true;
}

bool confidence_filter_init(ConfidenceFilter *filter,
                            const ConfidenceFilterConfig *cfg,
                            uint32_t now_ms) {
    if (filter == NULL || !confidence_config_valid(cfg)) {
        return false;
    }
    filter->cfg = cfg;
    filter->integrated_score = 0.0f;
    filter->history_mask = 0U;
    filter->state_entered_ms = now_ms;
    filter->last_update_ms = now_ms;
    /* Холодний старт: якщо об'єкт уже стоїть перед камерою в мить подачі живлення,
     * фільтру треба кілька тактів на розгін S[k]. Для критичних апаратів безпечніше
     * почати з увімкненої тривоги й дати автомату самому її зняти. */
    filter->is_active = cfg->fail_safe_start;
    return true;
}

float confidence_calibrate(float logit_target, float logit_bg, float temperature) {
    const float temp = (temperature > 0.0f && isfinite(temperature)) ? temperature : 1.0f;
    const float scaled_target = logit_target / temp;
    const float scaled_bg = logit_bg / temp;

    const float max_l = (scaled_target > scaled_bg) ? scaled_target : scaled_bg;
    const float exp_target = expf(scaled_target - max_l);
    const float exp_bg = expf(scaled_bg - max_l);

    const float sum = exp_target + exp_bg;
    /* Один з доданків після віднімання максимуму завжди дорівнює 1.0,
     * тож сума не може бути нулем — але детектор здатен віддати NaN. */
    if (!(sum > 0.0f)) {
        return 0.0f;
    }
    return exp_target / sum;
}

bool confidence_filter_update(ConfidenceFilter *filter, float raw_prob, uint32_t now_ms) {
    if (filter == NULL || filter->cfg == NULL) {
        return false;
    }
    const ConfidenceFilterConfig *cfg = filter->cfg;

    /* Затискання входу. Порівняння через заперечення ловить і NaN: одне-єдине
     * NaN з детектора отруїло б інтегратор назавжди, бо NaN * alpha = NaN. */
    float p = raw_prob;
    if (!(p >= 0.0f)) {
        p = 0.0f;
    } else if (p > 1.0f) {
        p = 1.0f;
    }

    /* 1. Інтегратор витоку: S[k] = alpha * S[k-1] + (1 - alpha) * P[k]. */
    filter->integrated_score = cfg->alpha * filter->integrated_score
                             + (1.0f - cfg->alpha) * p;

    /* 2. Ковзне бітове вікно: кадр квантується в один біт і в'їжджає зсувом. */
    const bool frame_hit = (p >= cfg->thresh_off);
    filter->history_mask = (filter->history_mask << 1) | (frame_hit ? 1U : 0U);

    const unsigned votes = popcount32(filter->history_mask & window_mask(cfg->window_size));
    const bool vote_passed = (votes >= (unsigned)cfg->min_votes);

    /* 3. Автомат із подвійним гістерезисом і таймером утримання. */
    if (filter->is_active) {
        /* Різниця беззнакових коректна і при переповненні лічильника мілісекунд
         * (32 біти вичерпуються приблизно за 49.7 доби безперервної роботи). */
        const bool hold_expired = (uint32_t)(now_ms - filter->state_entered_ms) >= cfg->min_hold_ms;
        if (hold_expired && filter->integrated_score < cfg->thresh_off && !vote_passed) {
            filter->is_active = false;
            filter->state_entered_ms = now_ms;
        }
    } else {
        if (filter->integrated_score >= cfg->thresh_on || vote_passed) {
            filter->is_active = true;
            filter->state_entered_ms = now_ms;
        }
    }

    filter->last_update_ms = now_ms;
    return filter->is_active;
}

bool confidence_filter_update_logits(ConfidenceFilter *filter,
                                     float logit_target,
                                     float logit_bg,
                                     uint32_t now_ms) {
    if (filter == NULL || filter->cfg == NULL) {
        return false;
    }
    const float p = confidence_calibrate(logit_target, logit_bg, filter->cfg->temperature);
    return confidence_filter_update(filter, p, now_ms);
}

uint32_t confidence_filter_window(const ConfidenceFilter *filter) {
    if (filter == NULL || filter->cfg == NULL) {
        return 0U;
    }
    return filter->history_mask & window_mask(filter->cfg->window_size);
}

unsigned confidence_filter_votes(const ConfidenceFilter *filter) {
    return popcount32(confidence_filter_window(filter));
}

uint32_t confidence_filter_idle_ms(const ConfidenceFilter *filter, uint32_t now_ms) {
    if (filter == NULL) {
        return 0U;
    }
    return (uint32_t)(now_ms - filter->last_update_ms);
}
