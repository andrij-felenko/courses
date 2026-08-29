#ifndef BATTERY_H
#define BATTERY_H

/* Модель первинної хімічної комірки.
 *
 * Усе, що тут лежить, береться з даташиту конкретного елемента: розрядна
 * крива, температурна таблиця ємності, внутрішній опір, саморозряд.
 * Жирний напис «2400 мА·год» на етикетці в розрахунок не входить сам по
 * собі — він лише перша цифра водоспаду втрат.
 *
 * Заголовок базовий: решта модулів включають його заради est_status.
 */

#include <stddef.h>

/* Коди помилок усього калькулятора. */
typedef enum {
    EST_OK = 0,
    EST_ERR_NULL,          /* не передано обов'язкову структуру */
    EST_ERR_CAPACITY,      /* ємність або еталонний струм не додатні */
    EST_ERR_VOLTAGE,       /* напруга або внутрішній опір не додатні */
    EST_ERR_CURVE,         /* розрядна крива не впорядкована за спаданням OCV */
    EST_ERR_TEMP_CURVE,    /* температурна таблиця не впорядкована за зростанням */
    EST_ERR_PEUKERT,       /* експонента Пейкерта поза [1.0, 2.0] */
    EST_ERR_NO_PHASES,     /* у циклі немає жодної активної фази */
    EST_ERR_TOO_MANY,      /* фаз більше, ніж уміщає масив результату */
    EST_ERR_PHASE_TIME,    /* тривалість фази не додатна */
    EST_ERR_PHASE_CURRENT, /* від'ємний струм фази */
    EST_ERR_PERIOD,        /* активні фази не влазять у період */
    EST_ERR_CUTOFF,        /* поріг відсічки вищий за напругу свіжої комірки */
    EST_ERR_NO_DRAIN       /* сумарний струм нульовий — ділити нема на що */
} est_status;

const char *est_status_str(est_status s);

/* Точка розрядної кривої з даташиту.
 * ocv_v     — напруга розімкненого кола комірки;
 * delivered — яка частка паспортної ємності вже віддана на момент, коли
 *             напруга розімкненого кола впала до цієї позначки.
 * Масив упорядкований за СПАДАННЯМ напруги, delivered — не спадає. */
typedef struct {
    double ocv_v;
    double delivered;
} bat_curve_point;

/* Точка температурної залежності доступної ємності (за зростанням температури). */
typedef struct {
    double temp_c;
    double factor;
} bat_temp_point;

typedef struct {
    const char *name;

    double capacity_mah;           /* паспортна ємність */
    double ocv_fresh_v;            /* напруга розімкненого кола свіжої комірки */
    double reference_current_ma;   /* струм, за якого паспортну ємність виміряли */

    double r_int_20c_ohm;          /* внутрішній опір за +20 °C */
    double r_int_beta_k;           /* B-константа температурної залежності опору */

    double peukert_k;              /* експонента Пейкерта */
    double relax_time_s;           /* стала часу релаксації іонів між імпульсами */

    double self_discharge_pct_year; /* саморозряд за +20 °C, % на рік */

    double passivation_max_factor; /* у скільки разів росте R_int на зрілій плівці LiCl */
    double passivation_onset_days; /* спокій, за який плівка виростає повністю */

    const bat_curve_point *curve;  /* розрядна крива */
    size_t curve_len;
    const bat_temp_point *temp_curve; /* температурна таблиця ємності */
    size_t temp_len;
} battery_t;

/* Перевіряє, що даташит переписали без помилок. */
est_status battery_validate(const battery_t *b);

/* Внутрішній опір за заданої температури (закон Арреніуса в NTC-формі). */
double battery_r_int(const battery_t *b, double temp_c);

/* Множник опору від пасиваційної плівки після idle_days спокою. */
double battery_passivation_factor(const battery_t *b, double idle_days);

/* Частка ємності, яку комірка встигає віддати, поки її OCV падає до ocv_v.
 * Це і є η_cutoff: усе, що лишилося нижче, для схеми недосяжне. */
double battery_delivered_above(const battery_t *b, double ocv_v);

/* Обернена задача: якою буде OCV, коли віддано частку delivered. */
double battery_ocv_at(const battery_t *b, double delivered);

/* Температурний коефіцієнт ємності η_temp. */
double battery_temp_factor(const battery_t *b, double temp_c);

/* Еквівалентний струм саморозряду (мА) за заданої температури.
 * Швидкість реакції подвоюється на кожні 10 °C (правило Арреніуса). */
double battery_self_discharge_ma(const battery_t *b, double temp_c);

/* У скільки разів дорожче обходиться заряд, узятий струмом current_ma,
 * порівняно з паспортним еталонним струмом (закон Пейкерта).
 * Нижче еталонного струму бонусу не рахуємо: паспорт його не гарантує. */
double battery_peukert_cost(const battery_t *b, double current_ma);

#endif /* BATTERY_H */
