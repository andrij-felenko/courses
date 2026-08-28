#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Конфігурація фільтра впевненості */
typedef struct {
    float alpha;               /* Коефіцієнт згладжування EMA (0.0 < alpha < 1.0) */
    float thresh_on;           /* Поріг активації тривоги (H_on, наприклад 0.75) */
    float thresh_off;          /* Поріг деактивації тривоги (H_off, наприклад 0.35) */
    uint32_t min_hold_ms;      /* Мінімальний час утримання активного стану (мс) */
    uint8_t window_size;       /* Розмір вікна M-з-N (макс 32 кадри) */
    uint8_t min_votes;         /* Поріг голосування M (кількість кадрів) */
} ConfidenceFilterConfig;

/* Стан екземпляра фільтра */
typedef struct {
    ConfidenceFilterConfig cfg;
    float integrated_score;    /* Поточна накопичена впевненість */
    uint32_t history_mask;     /* Бітова історія для M-з-N вікна */
    uint32_t state_entered_ms; /* Часова мітка останнього переходу стану */
    bool is_active;            /* Поточний стабільний дискретний вихід */
} ConfidenceFilter;

/* Ініціалізація структури фільтра з заданою конфігурацією */
void confidence_filter_init(ConfidenceFilter *filter, const ConfidenceFilterConfig *cfg) {
    if (!filter || !cfg) return;
    filter->cfg = *cfg;
    filter->integrated_score = 0.0f;
    filter->history_mask = 0U;
    filter->state_entered_ms = 0U;
    filter->is_active = false;
}

/* Обчислення каліброваної ймовірності через температурне масштабування */
float calibrate_temperature(float logit_target, float logit_bg, float temperature) {
    if (temperature <= 0.001f) temperature = 1.0f;
    float scaled_target = logit_target / temperature;
    float scaled_bg = logit_bg / temperature;
    
    /* Захист від переповнення експоненти */
    float max_l = (scaled_target > scaled_bg) ? scaled_target : scaled_bg;
    float exp_target = expf(scaled_target - max_l);
    float exp_bg = expf(scaled_bg - max_l);
    
    return exp_target / (exp_target + exp_bg);
}

/* Обробка нового такту виміру */
bool confidence_filter_update(ConfidenceFilter *filter, float raw_prob, uint32_t now_ms) {
    if (!filter) return false;

    /* 1. Інтегратор витоку (Exponential Moving Average) */
    filter->integrated_score = (filter->cfg.alpha * filter->integrated_score) +
                               ((1.0f - filter->cfg.alpha) * raw_prob);

    /* 2. Ковзне бітове вікно голосування M-з-N */
    bool frame_detected = (raw_prob >= filter->cfg.thresh_off);
    filter->history_mask = (filter->history_mask << 1) | (frame_detected ? 1U : 0U);
    
    /* Маскування за розміром вікна (захист при window_size = 32) */
    uint32_t valid_mask = (filter->cfg.window_size >= 32) ? 0xFFFFFFFFU :
                          ((1U << filter->cfg.window_size) - 1U);
    uint32_t current_window = filter->history_mask & valid_mask;
    
    /* Швидкий підрахунок кількості одиниць у бітовій масці */
    int votes = __builtin_popcount(current_window);
    bool vote_passed = (votes >= (int)filter->cfg.min_votes);

    /* 3. Автомат гістерезису з урахуванням мінімального часу утримання */
    if (filter->is_active) {
        /* Умови виходу з активного стану:
         * 1) Сплив мінімальний час утримання t_hold
         * 2) Накопичена впевненість впала нижче H_off ТА голосування не пройшло */
        bool hold_expired = (now_ms - filter->state_entered_ms) >= filter->cfg.min_hold_ms;
        if (hold_expired && (filter->integrated_score < filter->cfg.thresh_off) && !vote_passed) {
            filter->is_active = false;
            filter->state_entered_ms = now_ms;
        }
    } else {
        /* Умова входу в активний стан:
         * Накопичена впевненість перевищила H_on АБО голосування M-з-N впевнено пройшло */
        if ((filter->integrated_score >= filter->cfg.thresh_on) || vote_passed) {
            filter->is_active = true;
            filter->state_entered_ms = now_ms;
        }
    }

    return filter->is_active;
}
