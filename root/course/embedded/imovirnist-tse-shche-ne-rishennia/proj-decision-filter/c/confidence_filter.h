#ifndef CONFIDENCE_FILTER_H
#define CONFIDENCE_FILTER_H

#include <stdbool.h>
#include <stdint.h>

/* Історія голосування живе в одному 32-бітному слові, тож глибше вікно неможливе. */
#define CONFIDENCE_WINDOW_MAX 32u

/* Налаштування конвеєра. Структура ОДНА на всі фільтри системи: тримати копію
 * конфігурації в кожному з 32 треків — це 32 копії тих самих порогів у RAM. */
typedef struct {
    float    temperature;     /* T для калібрування логітів, T > 0 (типово 1.5..3.0) */
    float    alpha;           /* Коефіцієнт витоку EMA, 0 < alpha < 1 */
    float    thresh_on;       /* H_on — поріг активації за накопиченою впевненістю */
    float    thresh_off;      /* H_off — поріг деактивації і поріг біта голосування */
    uint32_t min_hold_ms;     /* t_hold — мінімальна тривалість активного стану */
    uint8_t  window_size;     /* N — глибина вікна голосування, 1..32 кадри */
    uint8_t  min_votes;       /* M — скільки кадрів з N підтверджують детекцію */
    bool     fail_safe_start; /* Холодний старт одразу в активному (безпечному) стані */
} ConfidenceFilterConfig;

/* Стан одного фільтра — рівно 24 байти на 32-бітній платформі:
 * 4 (вказівник) + 4 + 4 + 4 + 4 + 1 байт стану, вирівняний до 24. */
typedef struct {
    const ConfidenceFilterConfig *cfg;
    float    integrated_score;  /* S[k] — вихід інтегратора витоку */
    uint32_t history_mask;      /* Бітова історія кадрів, наймолодший біт — останній */
    uint32_t state_entered_ms;  /* Мітка часу останнього переходу автомата */
    uint32_t last_update_ms;    /* Мітка часу останнього такту (для таймауту треку) */
    bool     is_active;         /* Стабільний дискретний вихід: тривога чи норма */
} ConfidenceFilter;

/* Перевірка конфігурації. Зловити безглузді пороги треба ОДИН раз на старті,
 * а не в кожному такті: у гарячому шляху перевірок немає навмисно. */
bool confidence_config_valid(const ConfidenceFilterConfig *cfg);

/* Ініціалізація фільтра. Конфігурація не копіюється — фільтр тримає на неї
 * вказівник, тож вона мусить пережити фільтр (типово це static const об'єкт).
 * Повертає false, якщо конфігурація непридатна: тоді фільтр НЕ вмикають. */
bool confidence_filter_init(ConfidenceFilter *filter,
                            const ConfidenceFilterConfig *cfg,
                            uint32_t now_ms);

/* Температурне калібрування пари логітів «об'єкт проти фону» в імовірність.
 * Віднімання максимуму тримає аргумент expf() у межах (-inf, 0] — переповнення
 * до +inf неможливе за побудовою. */
float confidence_calibrate(float logit_target, float logit_bg, float temperature);

/* Один такт конвеєра з уже готовою ймовірністю: EMA -> вікно M-з-N -> автомат.
 * Повертає стабільний вихід ПІСЛЯ цього такту. */
bool confidence_filter_update(ConfidenceFilter *filter, float raw_prob, uint32_t now_ms);

/* Той самий такт, але від сирих логітів мережі: калібрування вбудоване. */
bool confidence_filter_update_logits(ConfidenceFilter *filter,
                                     float logit_target,
                                     float logit_bg,
                                     uint32_t now_ms);

/* Поточне вікно голосування, обрізане до window_size бітів (для діагностики). */
uint32_t confidence_filter_window(const ConfidenceFilter *filter);

/* Кількість підтверджень у поточному вікні. */
unsigned confidence_filter_votes(const ConfidenceFilter *filter);

/* Скільки мілісекунд минуло від останнього такту цього фільтра. */
uint32_t confidence_filter_idle_ms(const ConfidenceFilter *filter, uint32_t now_ms);

static inline float confidence_filter_score(const ConfidenceFilter *filter) {
    return filter->integrated_score;
}

static inline bool confidence_filter_active(const ConfidenceFilter *filter) {
    return filter->is_active;
}

#endif /* CONFIDENCE_FILTER_H */
