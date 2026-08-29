/* Модель шпаруватості автономного вузла.
 *
 * Рахує те, чим інженер користується під час вибору робочої точки:
 *   - коефіцієнт заповнення D та середній інтегральний струм I_avg;
 *   - розподіл заряду між активним спалахом і сном;
 *   - автономність від заданого джерела живлення;
 *   - точку енергетичної рівноваги (k = 1) і точку насичення T_90 (k = 9);
 *   - обернену задачу: мінімальний період T_min під цільовий термін служби;
 *   - регуляторний ліміт часу в ефірі за ETSI EN 300 220 (смуги EU868).
 *
 * Усі струми — у мікроамперах, увесь час — у секундах: одна система одиниць
 * на весь модуль дешевша за розсипані по коду множення на 1000.
 */
#ifndef DUTY_CYCLE_H
#define DUTY_CYCLE_H

#include <stdbool.h>

typedef enum {
    DUTY_OK = 0,
    DUTY_ERR_ARGS,        /* порожній вказівник */
    DUTY_ERR_PERIOD,      /* період не додатний або NaN */
    DUTY_ERR_WINDOW,      /* активне вікно порожнє або довше за період */
    DUTY_ERR_CURRENT,     /* порушено 0 <= I_sleep < I_on */
    DUTY_ERR_BATTERY,     /* ємність або коефіцієнт віддачі поза межами */
    DUTY_ERR_TARGET,      /* цільовий термін служби не додатний */
    DUTY_ERR_UNREACHABLE  /* мети не досягти за жодного періоду */
} duty_status;

const char *duty_strerror(duty_status st);

typedef struct {
    double i_on_ua;      /* струм активної фази (ядро + радіо), мкА */
    double t_on_s;       /* тривалість активного вікна t_on, с */
    double i_sleep_ua;   /* струм спокою I_sleep, мкА */
    double period_s;     /* повний період повторення T, с */
    double capacity_mah; /* номінальна ємність джерела, мА·год */
    double derating;     /* коефіцієнт корисної віддачі ємності, 0..1 */
} duty_config;

typedef struct {
    double duty;              /* D = t_on / T */
    double i_avg_ua;          /* середній інтегральний струм, мкА */
    double q_on_uas;          /* заряд активної фази за цикл, мкА·с */
    double q_off_uas;         /* заряд фази сну за цикл, мкА·с */
    double active_share_pct;  /* частка заряду на активну фазу, % */
    double sleep_share_pct;   /* частка заряду на сон, % */
    double k_energy;          /* k = Q_off / Q_on */
    double lifetime_h;        /* автономність, год */
    double lifetime_years;    /* автономність, років */
    double t_eq_s;            /* точка енергетичної рівноваги, с */
    double t_sat_s;           /* точка насичення T_90, с */
} duty_result;

/* Пряма задача: за конфігурацією циклу порахувати профіль споживання. */
duty_status duty_evaluate(const duty_config *cfg, duty_result *out);

/* Обернена задача: найкоротший період T, за якого вузол ще дотягує
 * до target_years. Струм спокою задає стелю: коли він сам вичерпує
 * бюджет, відповіді не існує — DUTY_ERR_UNREACHABLE. */
duty_status duty_min_period(const duty_config *cfg, double target_years, double *period_s);

/* --- Регуляторний бік: ліміт часу в ефірі (ETSI EN 300 220, EU868) --- */

typedef struct {
    const char *name;    /* позначення піддіапазону: g1, g2, g3 */
    double f_lo_mhz;
    double f_hi_mhz;
    double duty_limit;   /* частка години: 0.01 = 1 % */
    double max_erp_dbm;  /* стеля потужності, дБм */
} etsi_band;

#define ETSI_EU868_COUNT 3
extern const etsi_band ETSI_EU868[ETSI_EU868_COUNT];

/* Смуга, у яку потрапляє частота; NULL — частота поза EU868. */
const etsi_band *etsi_band_for(double freq_mhz);

typedef struct {
    double allowance_s;       /* дозволений час випромінювання за годину */
    double used_s;            /* фактичний час в ефірі за годину */
    double used_pct;          /* відсоток вичерпаного годинного ліміту */
    double packet_share_pct;  /* яку частку ліміту з'їдає ОДИН пакет */
    double packets_per_hour;  /* скільки таких пакетів дозволяє смуга */
    double min_period_s;      /* мінімальний період, дозволений регулятором */
    bool compliant;           /* чи вкладається обраний період у ліміт */
} airtime_check;

/* toa_s — час в ефірі одного пакета (Time-on-Air), НЕ все активне вікно:
 * регулятор рахує лише випромінювання, а не пробудження й обчислення. */
duty_status duty_check_airtime(const etsi_band *band, double toa_s,
                               double period_s, airtime_check *out);

#endif /* DUTY_CYCLE_H */
