#include "metric.h"

#include <math.h>
#include <string.h>

#define EMA_ALPHA 0.20f
#define MIN_DT_S  0.005f

/* Горизонт прогнозу — рівно ті дві хвилини, що їх мав оператор із зав'язки статті.
   Показник ще в зеленій зоні, але падіння вже незворотне: це критична подія. */
#define CRIT_HORIZON_S 120.0f

static bool beyond(float v, float limit, MetricDirection d)
{
    return (d == METRIC_RISING) ? (v >= limit) : (v <= limit);
}

/* Зняття тривоги вимагає ще й гістерезису — інакше на самій межі колір
   блимав би щосекунди, а мигтіння втомлює око швидше за будь-який шум. */
static bool released(float v, float limit, float hyst, MetricDirection d)
{
    return (d == METRIC_RISING) ? (v < limit - hyst) : (v > limit + hyst);
}

void metric_init(MetricChannel *m, const MetricConfig *cfg)
{
    memset(m, 0, sizeof(*m));
    m->cfg = *cfg;
    m->severity = SEV_NORMAL;
    m->seconds_to_limit = INFINITY;
}

/* Скільки секунд лишилось до критичного ліміту за поточним трендом. */
static void predict(MetricChannel *m)
{
    const MetricConfig *c = &m->cfg;
    float margin = (c->direction == METRIC_RISING) ? (c->crit_limit - m->value)
                                                   : (m->value - c->crit_limit);
    if (margin <= 0.0f) {
        m->seconds_to_limit = 0.0f;
    } else if (m->drift_rate <= 1e-6f) {
        m->seconds_to_limit = INFINITY;   /* стоїть або йде від межі */
    } else {
        m->seconds_to_limit = margin / m->drift_rate;
    }
}

static AlertSeverity raw_level(const MetricChannel *m)
{
    const MetricConfig *c = &m->cfg;

    if (beyond(m->value, c->crit_limit, c->direction)) {
        return SEV_CRITICAL;
    }
    /* Тихий дрейф: цифра ще в нормі, але ліміт буде за дві хвилини. Саме цей
       випадок людина не бачить — похідна яскравості нижча за поріг сітківки. */
    if (m->seconds_to_limit <= CRIT_HORIZON_S) {
        return SEV_CRITICAL;
    }
    if (beyond(m->value, c->warn_limit, c->direction)) {
        return SEV_WARNING;
    }
    if (c->max_drift_rate > 0.0f && m->drift_rate >= c->max_drift_rate) {
        return SEV_WARNING;
    }
    return SEV_NORMAL;
}

static void update_severity(MetricChannel *m)
{
    const MetricConfig *c = &m->cfg;
    AlertSeverity next = raw_level(m);

    if (next >= m->severity) {
        m->severity = next;
        return;
    }
    if (m->severity == SEV_CRITICAL &&
        !released(m->value, c->crit_limit, c->hysteresis, c->direction) &&
        beyond(m->value, c->crit_limit, c->direction)) {
        return;
    }
    if (next == SEV_NORMAL &&
        beyond(m->value, c->warn_limit, c->direction) &&
        !released(m->value, c->warn_limit, c->hysteresis, c->direction)) {
        return;
    }
    m->severity = next;
}

bool metric_update(MetricChannel *m, float raw, uint32_t now_ms)
{
    if (!isfinite(raw)) {
        return false;   /* NaN з побитого кадру MAVLink у фільтр не пускаємо */
    }
    if (m->has_sample && (int32_t)(now_ms - m->last_update_ms) < 0) {
        m->has_sample = false;   /* час пішов назад — джерело перезапустилось */
    }

    if (m->has_sample) {
        float dt = (float)(now_ms - m->last_update_ms) / 1000.0f;
        if (dt >= MIN_DT_S) {
            float toward = (m->cfg.direction == METRIC_RISING) ? (raw - m->value)
                                                               : (m->value - raw);
            float rate = toward / dt;
            m->drift_rate = EMA_ALPHA * rate + (1.0f - EMA_ALPHA) * m->drift_rate;
        }
    }

    m->value = raw;
    m->last_update_ms = now_ms;
    m->has_sample = true;
    m->stale = false;

    predict(m);
    update_severity(m);
    return true;
}

void metric_tick(MetricChannel *m, uint32_t now_ms)
{
    if (!m->has_sample || m->cfg.stale_after_ms == 0) {
        return;
    }
    m->stale = metric_silence_ms(m, now_ms) >= m->cfg.stale_after_ms;
}

uint32_t metric_silence_ms(const MetricChannel *m, uint32_t now_ms)
{
    if (!m->has_sample) {
        return 0;
    }
    return (uint32_t)(now_ms - m->last_update_ms);
}

const char *severity_name(AlertSeverity s)
{
    switch (s) {
    case SEV_CRITICAL: return "КРИТИЧНО";
    case SEV_WARNING:  return "УВАГА";
    default:           return "норма";
    }
}
