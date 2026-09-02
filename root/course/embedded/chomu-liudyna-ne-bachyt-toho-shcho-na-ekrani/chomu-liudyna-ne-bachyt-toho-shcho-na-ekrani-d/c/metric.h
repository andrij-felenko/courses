#ifndef METRIC_H
#define METRIC_H

#include <stdbool.h>
#include <stdint.h>

/* Куди від норми лежить небезпека для цього показника. Без цього поля детектор
   вміє ловити лише зростання — а батарея, тиск і рівень сигналу падають. */
typedef enum {
    METRIC_RISING = 0,   /* небезпечно вгору: температура, струм, HDOP */
    METRIC_FALLING       /* небезпечно вниз: напруга банки, RSSI, тиск */
} MetricDirection;

typedef enum {
    SEV_NORMAL = 0,
    SEV_WARNING,
    SEV_CRITICAL
} AlertSeverity;

typedef struct {
    const char *name;
    const char *unit;
    MetricDirection direction;
    float warn_limit;
    float crit_limit;
    float max_drift_rate;    /* од/с у бік небезпеки; 0 — детектор дрейфу вимкнено */
    float hysteresis;        /* од; на стільки треба відійти назад, щоб знизити рівень */
    uint32_t stale_after_ms; /* без нових вибірок довше — дані застигли; 0 — не стежити */
} MetricConfig;

typedef struct {
    MetricConfig cfg;
    float value;
    float drift_rate;        /* EMA похідної; знак «+» означає рух У БІК небезпеки */
    float seconds_to_limit;  /* прогноз до crit_limit; INFINITY — не наближається */
    AlertSeverity severity;
    bool stale;
    bool has_sample;
    uint32_t last_update_ms;
} MetricChannel;

void metric_init(MetricChannel *m, const MetricConfig *cfg);

/* Приймає вибірку телеметрії. false — вибірку відкинуто (NaN у кадрі, час пішов
   назад): стан каналу лишається попереднім, і його підбере старіння. */
bool metric_update(MetricChannel *m, float raw, uint32_t now_ms);

/* Хід годинника без даних: тільки так виявляється мовчання джерела. */
void metric_tick(MetricChannel *m, uint32_t now_ms);

uint32_t metric_silence_ms(const MetricChannel *m, uint32_t now_ms);
const char *severity_name(AlertSeverity s);

#endif /* METRIC_H */
