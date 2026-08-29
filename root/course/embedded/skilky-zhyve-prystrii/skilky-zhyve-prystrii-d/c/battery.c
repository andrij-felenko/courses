#include "battery.h"

#include <math.h>

#define HOURS_PER_YEAR 8766.0    /* 365.25 доби · 24 год */
#define KELVIN_ZERO    273.15
#define KELVIN_REF     293.15    /* +20 °C — умови паспортних вимірювань */
#define ARRHENIUS_Q10  2.0       /* швидкість реакції подвоюється на кожні 10 °C */

const char *est_status_str(est_status s)
{
    switch (s) {
    case EST_OK:                return "гаразд";
    case EST_ERR_NULL:          return "не передано обов'язкову структуру";
    case EST_ERR_CAPACITY:      return "ємність або еталонний струм не додатні";
    case EST_ERR_VOLTAGE:       return "напруга або внутрішній опір не додатні";
    case EST_ERR_CURVE:         return "розрядна крива не впорядкована за спаданням напруги";
    case EST_ERR_TEMP_CURVE:    return "температурна таблиця не впорядкована за зростанням";
    case EST_ERR_PEUKERT:       return "експонента Пейкерта поза межами [1.0, 2.0]";
    case EST_ERR_NO_PHASES:     return "у робочому циклі немає жодної активної фази";
    case EST_ERR_TOO_MANY:      return "фаз більше, ніж уміщає масив результату";
    case EST_ERR_PHASE_TIME:    return "тривалість фази не додатна";
    case EST_ERR_PHASE_CURRENT: return "від'ємний струм фази";
    case EST_ERR_PERIOD:        return "активні фази не влазять у період циклу";
    case EST_ERR_CUTOFF:        return "поріг відсічки вищий за напругу свіжої комірки";
    case EST_ERR_NO_DRAIN:      return "сумарний струм нульовий — час життя нескінченний";
    }
    return "невідома помилка";
}

static double clampd(double v, double lo, double hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

est_status battery_validate(const battery_t *b)
{
    size_t i;

    if (!b || !b->curve || !b->temp_curve)
        return EST_ERR_NULL;
    if (b->capacity_mah <= 0.0 || b->reference_current_ma <= 0.0)
        return EST_ERR_CAPACITY;
    if (b->ocv_fresh_v <= 0.0 || b->r_int_20c_ohm <= 0.0)
        return EST_ERR_VOLTAGE;
    if (b->peukert_k < 1.0 || b->peukert_k > 2.0)
        return EST_ERR_PEUKERT;

    if (b->curve_len < 2)
        return EST_ERR_CURVE;
    for (i = 1; i < b->curve_len; ++i) {
        /* напруга мусить спадати, віддана частка — не спадати */
        if (b->curve[i].ocv_v >= b->curve[i - 1].ocv_v)
            return EST_ERR_CURVE;
        if (b->curve[i].delivered < b->curve[i - 1].delivered)
            return EST_ERR_CURVE;
    }
    if (b->curve[0].delivered < 0.0 || b->curve[b->curve_len - 1].delivered > 1.0)
        return EST_ERR_CURVE;

    if (b->temp_len < 2)
        return EST_ERR_TEMP_CURVE;
    for (i = 1; i < b->temp_len; ++i) {
        if (b->temp_curve[i].temp_c <= b->temp_curve[i - 1].temp_c)
            return EST_ERR_TEMP_CURVE;
        if (b->temp_curve[i].factor < 0.0 || b->temp_curve[i].factor > 1.0)
            return EST_ERR_TEMP_CURVE;
    }
    return EST_OK;
}

double battery_r_int(const battery_t *b, double temp_c)
{
    double t_k = temp_c + KELVIN_ZERO;

    /* Нижче рідкого азоту електроліт уже не рідина — там модель не працює,
     * але й ділити на нуль не даємо. */
    if (t_k < 100.0)
        t_k = 100.0;

    /* R(T) = R20 · exp(B · (1/T − 1/293.15)).
     * Для типової літієвої комірки з B ≈ 6300 K це дає паспортні
     * 0.5 Ом за +20 °C і майже 15 Ом за −20 °C. */
    return b->r_int_20c_ohm * exp(b->r_int_beta_k * (1.0 / t_k - 1.0 / KELVIN_REF));
}

double battery_passivation_factor(const battery_t *b, double idle_days)
{
    double growth;

    if (b->passivation_onset_days <= 0.0 || b->passivation_max_factor <= 1.0)
        return 1.0;
    if (idle_days <= 0.0)
        return 1.0;

    /* Плівка LiCl росте не лінійно, а приблизно як корінь із часу спокою:
     * товща плівка сама гальмує реакцію, що її нарощує. */
    growth = sqrt(clampd(idle_days / b->passivation_onset_days, 0.0, 1.0));
    return 1.0 + (b->passivation_max_factor - 1.0) * growth;
}

double battery_delivered_above(const battery_t *b, double ocv_v)
{
    const bat_curve_point *p = b->curve;
    size_t n = b->curve_len;
    size_t i;

    /* Поріг вищий за напругу свіжої комірки — вона мертва з першого дня. */
    if (ocv_v >= p[0].ocv_v)
        return p[0].delivered;
    if (ocv_v <= p[n - 1].ocv_v)
        return p[n - 1].delivered;

    for (i = 1; i < n; ++i) {
        if (ocv_v >= p[i].ocv_v) {
            double span = p[i - 1].ocv_v - p[i].ocv_v;
            double t = (span > 0.0) ? (p[i - 1].ocv_v - ocv_v) / span : 0.0;
            return p[i - 1].delivered + t * (p[i].delivered - p[i - 1].delivered);
        }
    }
    return p[n - 1].delivered;
}

double battery_ocv_at(const battery_t *b, double delivered)
{
    const bat_curve_point *p = b->curve;
    size_t n = b->curve_len;
    size_t i;

    if (delivered <= p[0].delivered)
        return p[0].ocv_v;
    if (delivered >= p[n - 1].delivered)
        return p[n - 1].ocv_v;

    for (i = 1; i < n; ++i) {
        if (delivered <= p[i].delivered) {
            double span = p[i].delivered - p[i - 1].delivered;
            double t = (span > 0.0) ? (delivered - p[i - 1].delivered) / span : 0.0;
            return p[i - 1].ocv_v + t * (p[i].ocv_v - p[i - 1].ocv_v);
        }
    }
    return p[n - 1].ocv_v;
}

double battery_temp_factor(const battery_t *b, double temp_c)
{
    const bat_temp_point *p = b->temp_curve;
    size_t n = b->temp_len;
    size_t i;

    if (temp_c <= p[0].temp_c)
        return p[0].factor;
    if (temp_c >= p[n - 1].temp_c)
        return p[n - 1].factor;

    for (i = 1; i < n; ++i) {
        if (temp_c <= p[i].temp_c) {
            double span = p[i].temp_c - p[i - 1].temp_c;
            double t = (span > 0.0) ? (temp_c - p[i - 1].temp_c) / span : 0.0;
            return p[i - 1].factor + t * (p[i].factor - p[i - 1].factor);
        }
    }
    return p[n - 1].factor;
}

double battery_self_discharge_ma(const battery_t *b, double temp_c)
{
    double accel = pow(ARRHENIUS_Q10, (temp_c - 20.0) / 10.0);
    double pct_year = b->self_discharge_pct_year * accel;

    /* Річний відсоток втрати ємності — це постійний віртуальний струм витоку. */
    return (b->capacity_mah * pct_year / 100.0) / HOURS_PER_YEAR;
}

double battery_peukert_cost(const battery_t *b, double current_ma)
{
    if (current_ma <= b->reference_current_ma)
        return 1.0;
    return pow(current_ma / b->reference_current_ma, b->peukert_k - 1.0);
}
