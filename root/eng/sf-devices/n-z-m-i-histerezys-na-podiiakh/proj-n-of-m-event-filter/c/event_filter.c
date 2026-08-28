/**
 * @file event_filter.c
 * @brief Реалізація алгоритмів фільтрації дискретних подій N-з-M на C99
 */

#include "event_filter.h"

/**
 * @brief Апаратний або безрозгалужений паралельний підрахунок одиниць
 */
static inline uint8_t popcount32(uint32_t val) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint8_t)__builtin_popcount(val);
#elif defined(_MSC_VER)
    return (uint8_t)__popcnt(val);
#else
    /* Портативний алгоритм бітового паралельного суматора за 12 операцій */
    val = val - ((val >> 1) & 0x55555555U);
    val = (val & 0x33333333U) + ((val >> 2) & 0x33333333U);
    return (uint8_t)((((val + (val >> 4)) & 0x0F0F0F0FU) * 0x01010101U) >> 24);
#endif
}

/* ========================================================================= */
/* Швидкісний однослівний фільтр (M <= 32)                                   */
/* ========================================================================= */

void event_filter_fast32_init(event_filter_fast32_t *f, 
                              const event_filter_config_t *cfg, 
                              bool initial_raw_level) 
{
    if (f == NULL || cfg == NULL) {
        return;
    }

    uint8_t m = (cfg->m_window > 32U || cfg->m_window == 0U) ? 32U : (uint8_t)cfg->m_window;
    uint8_t non = (cfg->n_on > m) ? m : (uint8_t)cfg->n_on;
    uint8_t noff = (cfg->n_off >= non) ? ((non > 0U) ? (non - 1U) : 0U) : (uint8_t)cfg->n_off;

    f->m_window = m;
    f->n_on = non;
    f->n_off = noff;
    f->output_state = initial_raw_level;
    f->dwell_counter = 0U;
    f->max_dwell_samples = cfg->max_dwell_samples;
    f->glitch_count = 0U;
    f->status_flags = EVENT_FILTER_STATUS_OK;

    /* Захист від UB при зсуві на 32 розряди */
    if (m == 32U) {
        f->window_mask = 0xFFFFFFFFU;
    } else {
        f->window_mask = (1U << m) - 1U;
    }

    /* Заповнення історії початковим рівнем для усунення холодного перехідного процесу */
    f->history = initial_raw_level ? f->window_mask : 0U;
}

bool event_filter_fast32_update(event_filter_fast32_t *f, bool raw_sample) {
    if (f == NULL) {
        return false;
    }

    /* Крок 1: Зсув бітової маски вліво та додавання нового біта */
    f->history = ((f->history << 1) | (raw_sample ? 1U : 0U)) & f->window_mask;

    /* Крок 2: Апаратний підрахунок кількості одиниць за 1 такт */
    uint8_t current_ones = popcount32(f->history);

    bool previous_state = f->output_state;

    /* Крок 3: Правило асиметричного гістерезису */
    if (current_ones >= f->n_on) {
        f->output_state = true;
    } else if (current_ones <= f->n_off) {
        f->output_state = false;
    }
    /* У мертвій зоні (n_off < current_ones < n_on) стан не змінюється */

    /* Крок 4: Фіксація відхиленої завади для телеметрії */
    if (raw_sample != f->output_state) {
        f->glitch_count++;
    }

    /* Крок 5: Детектор залипання сенсора (Stuck-at Fault) */
    if (f->output_state == previous_state) {
        if (f->max_dwell_samples > 0U) {
            f->dwell_counter++;
            if (f->dwell_counter >= f->max_dwell_samples) {
                f->status_flags |= f->output_state ? 
                    EVENT_FILTER_STATUS_STUCK_ACTIVE : EVENT_FILTER_STATUS_STUCK_INACTIVE;
            }
        }
    } else {
        /* При валідному переході скидаємо лічильник залипання */
        f->dwell_counter = 0U;
        f->status_flags &= (uint8_t)~(EVENT_FILTER_STATUS_STUCK_ACTIVE | EVENT_FILTER_STATUS_STUCK_INACTIVE);
    }

    return f->output_state;
}

bool event_filter_fast32_get_state(const event_filter_fast32_t *f) {
    return (f != NULL) ? f->output_state : false;
}

uint8_t event_filter_fast32_get_count(const event_filter_fast32_t *f) {
    return (f != NULL) ? popcount32(f->history) : 0U;
}

uint8_t event_filter_fast32_get_diagnostics(const event_filter_fast32_t *f, uint32_t *out_glitches) {
    if (f == NULL) {
        return EVENT_FILTER_STATUS_OK;
    }
    if (out_glitches != NULL) {
        *out_glitches = f->glitch_count;
    }
    return f->status_flags;
}

/* ========================================================================= */
/* Універсальний багатослівний фільтр (M до 1024)                             */
/* ========================================================================= */

void event_filter_multiword_init(event_filter_multiword_t *f, 
                                 const event_filter_config_t *cfg, 
                                 bool initial_raw_level) 
{
    if (f == NULL || cfg == NULL) {
        return;
    }

    uint16_t m = cfg->m_window;
    if (m == 0U || m > EVENT_FILTER_MAX_MULTIWORD_BITS) {
        m = EVENT_FILTER_MAX_MULTIWORD_BITS;
    }

    uint16_t non = (cfg->n_on > m) ? m : cfg->n_on;
    uint16_t noff = (cfg->n_off >= non) ? ((non > 0U) ? (non - 1U) : 0U) : cfg->n_off;

    f->m_window = m;
    f->n_on = non;
    f->n_off = noff;
    f->head_index = 0U;
    f->output_state = initial_raw_level;
    f->dwell_counter = 0U;
    f->max_dwell_samples = cfg->max_dwell_samples;
    f->glitch_count = 0U;
    f->status_flags = EVENT_FILTER_STATUS_OK;

    uint32_t fill_val = initial_raw_level ? 0xFFFFFFFFU : 0x00000000U;
    for (size_t i = 0; i < EVENT_FILTER_WORDS_CAPACITY; i++) {
        f->words[i] = fill_val;
    }

    f->current_popcount = initial_raw_level ? m : 0U;
}

bool event_filter_multiword_update(event_filter_multiword_t *f, bool raw_sample) {
    if (f == NULL) {
        return false;
    }

    /* 1. Пошук позиції біта в масиві */
    size_t word_idx = f->head_index / EVENT_FILTER_WORD_BITS;
    size_t bit_idx  = f->head_index % EVENT_FILTER_WORD_BITS;
    uint32_t mask   = 1U << bit_idx;

    /* 2. Зчитування старого біта перед перезаписом */
    bool old_bit = (f->words[word_idx] & mask) != 0U;

    /* 3. Запис нового значення */
    if (raw_sample) {
        f->words[word_idx] |= mask;
    } else {
        f->words[word_idx] &= ~mask;
    }

    /* 4. Інкрементальне O(1) оновлення лічильника суми */
    if (raw_sample && !old_bit) {
        f->current_popcount++;
    } else if (!raw_sample && old_bit) {
        f->current_popcount--;
    }

    /* 5. Просування кільцевого покажчика */
    f->head_index++;
    if (f->head_index >= f->m_window) {
        f->head_index = 0U;
    }

    /* 6. Гістерезис */
    bool prev_state = f->output_state;
    if (f->current_popcount >= f->n_on) {
        f->output_state = true;
    } else if (f->current_popcount <= f->n_off) {
        f->output_state = false;
    }

    /* 7. Діагностика */
    if (raw_sample != f->output_state) {
        f->glitch_count++;
    }

    if (f->output_state == prev_state) {
        if (f->max_dwell_samples > 0U) {
            f->dwell_counter++;
            if (f->dwell_counter >= f->max_dwell_samples) {
                f->status_flags |= f->output_state ? 
                    EVENT_FILTER_STATUS_STUCK_ACTIVE : EVENT_FILTER_STATUS_STUCK_INACTIVE;
            }
        }
    } else {
        f->dwell_counter = 0U;
        f->status_flags &= (uint8_t)~(EVENT_FILTER_STATUS_STUCK_ACTIVE | EVENT_FILTER_STATUS_STUCK_INACTIVE);
    }

    return f->output_state;
}

bool event_filter_multiword_get_state(const event_filter_multiword_t *f) {
    return (f != NULL) ? f->output_state : false;
}

uint16_t event_filter_multiword_get_count(const event_filter_multiword_t *f) {
    return (f != NULL) ? f->current_popcount : 0U;
}
