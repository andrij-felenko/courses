/* compass_mot.h — модель завади від струму: потокова компенсація і регресія OLS.
 *
 * Тут немає нічого про мотори й газ: цей модуль знає лише пару
 * «струм → відхилення поля». Стендовий прогін живе в calib_fsm.c.
 */
#ifndef COMPASS_MOT_H
#define COMPASS_MOT_H

#include <stdbool.h>
#include <stdint.h>

/* Тривісний вектор магнітної індукції, мкТл. */
typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

/* ---------------------------------------------------------------- */
/* Потоковий компенсатор: B_clean = B_meas − k · I_filt              */
/* ---------------------------------------------------------------- */

typedef struct {
    vec3_t k;                 /* коефіцієнти чутливості, мкТл/А          */
    float  lpf_alpha;         /* коефіцієнт однополюсного ФНЧ струму     */
    float  current_filtered;  /* стан фільтра, А                         */
    float  max_current_a;     /* понад це вважаємо давач збреханим       */
    bool   enabled;           /* нульові k → компенсувати нема чого      */
} compass_mot_t;

/* dt_sec — період польотного циклу, cutoff_hz — зріз ФНЧ струму (10–12 Гц). */
void   compass_mot_init(compass_mot_t *cm, vec3_t k,
                        float dt_sec, float cutoff_hz, float max_current_a);
void   compass_mot_set_k(compass_mot_t *cm, vec3_t k);
void   compass_mot_reset(compass_mot_t *cm);

/* Один такт: віддає очищене поле. Негативний, надмірний або нечисловий
 * струм — це збій давача, а не привід псувати компас: віддаємо сире поле. */
vec3_t compass_mot_apply(compass_mot_t *cm, vec3_t b_raw, float current_a);

/* ---------------------------------------------------------------- */
/* Накопичувач регресії найменших квадратів                          */
/* ---------------------------------------------------------------- */

/* Суми тримаємо в double: 1000 вибірок по I² з I до 150 А з'їдають
 * мантису float швидше, ніж здається. */
typedef struct {
    vec3_t   baseline;    /* B_base, знятий при зупинених моторах */
    double   sum_i;
    double   sum_i2;
    double   sum_b[3];    /* ∑ ΔB по осях          */
    double   sum_b2[3];   /* ∑ ΔB² — потрібне для R² */
    double   sum_ib[3];   /* ∑ (I · ΔB)            */
    float    i_max;       /* найбільший побачений струм */
    uint32_t n;
    uint32_t rejected;    /* відкинуті вибірки (NaN, від'ємний струм) */
} compass_mot_ols_t;

typedef enum {
    COMPASS_MOT_OK = 0,
    COMPASS_MOT_ERR_FEW_SAMPLES,   /* прогін обірвався надто рано        */
    COMPASS_MOT_ERR_NO_SPAN,       /* струм не змінювався — нахил не визначений */
    COMPASS_MOT_ERR_NO_FIELD,      /* базове поле ~0: компас мертвий     */
    COMPASS_MOT_ERR_SAVE           /* не записалося в енергонезалежну пам'ять */
} compass_mot_err_t;

typedef struct {
    vec3_t   k;                 /* мкТл/А                                */
    float    r2[3];             /* якість підгонки по осях, 0..1         */
    float    interference_pct;  /* ||ΔB(I_max)|| / ||B_base|| · 100%     */
    float    i_max;             /* струм, на якому оцінено заваду        */
    uint32_t samples;
} compass_mot_fit_t;

void compass_mot_ols_reset(compass_mot_ols_t *ols, vec3_t baseline);
void compass_mot_ols_feed(compass_mot_ols_t *ols, float current_a, vec3_t b_meas);
compass_mot_err_t compass_mot_ols_solve(const compass_mot_ols_t *ols,
                                        compass_mot_fit_t *out);

const char *compass_mot_strerror(compass_mot_err_t err);
/* Три смуги придатності компоновки за §3. */
const char *compass_mot_verdict(float interference_pct);

#endif /* COMPASS_MOT_H */
