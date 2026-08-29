#ifndef LIFETIME_H
#define LIFETIME_H

/* Зведення енергетичного бюджету: паспортна ємність → фактично доступна,
 * профіль циклу + саморозряд → сумарний струм, і звідси час автономності.
 *
 * Тут же живе перевірка імпульсної просадки: якщо напруга під час передачі
 * провалюється нижче порогу відсічки, жоден розрахунок годин не має сенсу —
 * пристрій піде в цикл перезавантажень із повною батареєю.
 */

#include "battery.h"
#include "dutycycle.h"

/* Умови експлуатації й вимоги схеми. */
typedef struct {
    double cutoff_v;        /* V_cutoff: поріг BOD плюс dropout стабілізатора */
    double temp_c;          /* робоча температура */
    double storage_days;    /* скільки комірка простояла в спокої до першого імпульсу */
    double safety_factor;   /* k_safe — інженерний запас на розкид і старіння */
} site_t;

/* Що обмежує термін служби першим. */
typedef enum {
    LIM_BROWNOUT,        /* просадка нижче відсічки — пристрій перезавантажується */
    LIM_SELF_DISCHARGE,  /* стеля хімії: комірка витікає швидше, ніж її споживають */
    LIM_ACTIVE_PHASE,    /* найдорожча фаза пробудження */
    LIM_SLEEP            /* струм сну разом зі струмом спокою стабілізатора */
} limiter_t;

const char *limiter_str(limiter_t l);

/* Аналіз імпульсу передавача. */
typedef struct {
    double r_int_ohm;        /* внутрішній опір за робочої температури */
    double sag_v;            /* ΔV = I_pulse · R_int */
    double v_term_v;         /* напруга на клемах під час імпульсу */
    int brownout;            /* просадка нижче порогу відсічки */

    double r_passivated_ohm; /* опір першого імпульсу після довгого спокою */
    double sag_storage_v;
    double v_term_storage_v;
    int brownout_after_storage;

    /* Буферна ємність, якщо просадка не влазить у бюджет напруги. */
    int buffer_needed;
    int buffer_impossible;   /* поріг вище за робоче плато — буфер не врятує */
    double buffer_farads;
    double buffer_esr_max_ohm;
    double headroom_v;       /* робоче плато мінус поріг відсічки */
} pulse_report_t;

typedef struct {
    /* Водоспад втрат ємності. */
    double eta_cutoff;
    double eta_temp;
    double eta_pulse;
    double ocv_cutoff_v;      /* OCV, за якої імпульс уперше провалює поріг */
    double c_after_cutoff_mah;
    double c_after_temp_mah;
    double c_eff_mah;

    /* Струми. */
    double i_avg_ma;
    double i_self_ma;
    double i_total_ma;

    /* Час. */
    double hours;
    double days;
    double years;
    double guaranteed_years;
    double naive_years;       /* паспортна ємність поділена на середній струм */
    double optimism_ratio;    /* у скільки разів наївна оцінка завищена */

    limiter_t limiter;
    const char *limiter_note;

    pulse_report_t pulse;
    duty_result_t duty;
} estimate_t;

est_status lifetime_estimate(const battery_t *b,
                             const duty_cycle_t *dc,
                             const site_t *site,
                             estimate_t *out);

#endif /* LIFETIME_H */
