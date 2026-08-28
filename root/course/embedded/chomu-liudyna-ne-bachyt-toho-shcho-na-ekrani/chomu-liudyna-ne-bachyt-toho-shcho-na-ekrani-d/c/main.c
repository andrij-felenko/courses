#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define EMA_ALPHA 0.20f

typedef enum {
    SEV_NORMAL = 0,
    SEV_WARNING,
    SEV_CRITICAL
} AlertSeverity;

typedef struct {
    float value;
    float filtered_rate;      /* Похідна dx/dt з фільтрацією EMA */
    uint32_t last_time_ms;
    float warn_limit;
    float crit_limit;
    float max_drift_rate;     /* Поріг швидкості для ловлі прихованого дрейфу */
    AlertSeverity severity;
} MetricChannel;

void metric_update(MetricChannel *m, float new_val, uint32_t now_ms) {
    if (m->last_time_ms > 0) {
        float dt = (now_ms - m->last_time_ms) / 1000.0f;
        if (dt > 0.005f) {
            float raw_rate = fabsf(new_val - m->value) / dt;
            m->filtered_rate = (EMA_ALPHA * raw_rate) + ((1.0f - EMA_ALPHA) * m->filtered_rate);
        }
    }
    m->value = new_val;
    m->last_time_ms = now_ms;

    /* Виявлення аварії: прямий перетин порогу або небезпечна швидкість дрейфу */
    if (m->value >= m->crit_limit) {
        m->severity = SEV_CRITICAL;
    } else if (m->value >= m->warn_limit || (m->max_drift_rate > 0 && m->filtered_rate >= m->max_drift_rate)) {
        m->severity = SEV_WARNING;
    } else {
        m->severity = SEV_NORMAL;
    }
}
