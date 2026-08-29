#include "diagnose.h"

/* Пороги відкалібровані для квадрокоптерів 5–10 дюймів на 4S–6S. */
#define TAU_LAGGY_MS       24.0
#define RISE_SLOW_MS       90.0
#define RISE_TWITCHY_MS    20.0
#define OVERSHOOT_HIGH_PCT 22.0
#define OVERSHOOT_FLAT_PCT 1.0
#define NOISE_WATCH        15.0
#define NOISE_HOT          35.0
#define RING_MANY          4

MetricBands diagnose_bands(const StepMetrics *m)
{
    MetricBands b;

    b.tau = (m->tau_ms > TAU_LAGGY_MS) ? BAND_UNDER : BAND_HEALTHY;

    if (!m->reached_90) {
        b.rise = BAND_UNDER;            /* до 90% так і не дотягнув */
    } else if (m->rise_time_ms > RISE_SLOW_MS) {
        b.rise = BAND_UNDER;
    } else if (m->rise_time_ms < RISE_TWITCHY_MS) {
        b.rise = BAND_OVER;
    } else {
        b.rise = BAND_HEALTHY;
    }

    if (m->overshoot_pct > OVERSHOOT_HIGH_PCT) {
        b.overshoot = BAND_OVER;
    } else if (m->overshoot_pct < OVERSHOOT_FLAT_PCT) {
        b.overshoot = BAND_UNDER;
    } else {
        b.overshoot = BAND_HEALTHY;
    }

    if (!m->noise_measured) {
        b.noise = BAND_UNKNOWN;
    } else if (m->d_noise_rms > NOISE_HOT) {
        b.noise = BAND_OVER;
    } else if (m->d_noise_rms > NOISE_WATCH) {
        b.noise = BAND_WATCH;
    } else {
        b.noise = BAND_HEALTHY;
    }

    return b;
}

TuneVerdict diagnose(const StepMetrics *m, MetricBands b)
{
    /* Порядок не довільний: поки затримка завелика, крутити P і D
       безглуздо — жорсткіший контур просто швидше зірветься. */
    if (b.tau == BAND_UNDER) {
        return TUNE_SYSTEM_LAGGY;
    }
    if (b.noise == BAND_OVER) {
        return TUNE_D_NOISE;
    }
    if (b.overshoot == BAND_OVER) {
        return (m->ring_crossings > RING_MANY) ? TUNE_P_HIGH : TUNE_D_LOW;
    }
    if (!m->settled) {
        return TUNE_NOT_SETTLED;
    }
    if (b.rise == BAND_OVER) {
        return TUNE_RISE_TOO_FAST;
    }
    if (b.rise == BAND_UNDER && b.overshoot == BAND_UNDER) {
        return TUNE_P_LOW;
    }
    if (b.overshoot == BAND_UNDER) {
        return TUNE_OVERDAMPED;
    }
    return TUNE_HEALTHY;
}

const char *band_mark(MetricBand b)
{
    switch (b) {
    case BAND_HEALTHY: return "норма";
    case BAND_WATCH:   return "пильнуй";
    case BAND_UNDER:   return "замало";
    case BAND_OVER:    return "забагато";
    default:           return "н/д";
    }
}

const char *verdict_title(TuneVerdict v)
{
    switch (v) {
    case TUNE_HEALTHY:       return "контур збалансовано";
    case TUNE_SYSTEM_LAGGY:  return "система млява: завелике транспортне запізнення";
    case TUNE_D_NOISE:       return "ВЧ-шум D-терма: мотори гріються даремно";
    case TUNE_P_HIGH:        return "завеликий P: дзвін навколо завдання";
    case TUNE_D_LOW:         return "замалий D: одиничний відскок без демпфування";
    case TUNE_RISE_TOO_FAST: return "надто різке наростання: ризик самозбудження";
    case TUNE_P_LOW:         return "замалий P: ватне керування";
    case TUNE_OVERDAMPED:    return "передемпфована реакція";
    case TUNE_NOT_SETTLED:   return "апарат не заспокоївся до кінця вікна";
    }
    return "невідомо";
}

const char *verdict_advice(TuneVerdict v)
{
    switch (v) {
    case TUNE_HEALTHY:
        return "лишити як є; повторити заміри на розрядженій батареї";
    case TUNE_SYSTEM_LAGGY:
        return "розширити смугу фільтрів гіроскопа або перейти на швидший протокол ESC (DShot600); нарощувати P і D зараз шкідливо";
    case TUNE_D_NOISE:
        return "зменшити K_d на 20% або увімкнути динамічний режекторний фільтр за обертами";
    case TUNE_P_HIGH:
        return "зменшити P на 15%: контур розгойдує сам себе";
    case TUNE_D_LOW:
        return "збільшити D на 10–15%: наростання швидке, бракує саме демпфування";
    case TUNE_RISE_TOO_FAST:
        return "зменшити P на 10%: на просілій батареї такий контур зірветься в самозбудження";
    case TUNE_P_LOW:
        return "збільшити P на 15–20%: апарат не встигає за завданням";
    case TUNE_OVERDAMPED:
        return "зменшити D на 10% або підняти P: реакція надто в'язка";
    case TUNE_NOT_SETTLED:
        return "подовжити маневр у тесті або шукати механічний резонанс: коливання не згасають";
    }
    return "";
}
