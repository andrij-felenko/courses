#include "edge_detector.h"

#include <math.h>

void edge_detector_init(edge_detector_t *dev, uint32_t now_ms)
{
    welford_reset(&dev->stats);
    ring_buffer_clear(&dev->snapshot);
    dev->last_tx_value     = 0.0f;
    dev->last_heartbeat_ms = now_ms;   /* не нуль: годинник RTOS міг стартувати не з нуля */
    dev->has_tx            = false;
}

void edge_detector_reset(edge_detector_t *dev, uint32_t now_ms)
{
    edge_detector_init(dev, now_ms);
}

uint32_t edge_detector_snapshot(const edge_detector_t *dev, float *dest, uint32_t dest_len)
{
    return ring_buffer_copy(&dev->snapshot, dest, dest_len);
}

telemetry_report_t edge_detector_process(edge_detector_t *dev,
                                         float raw_sample,
                                         uint32_t now_ms)
{
    telemetry_report_t out = {0};
    out.timestamp_ms = now_ms;
    out.value        = raw_sample;

    /* 0. Відмова давача. NaN або нескінченність приходять з обірваного входу
          АЦП і з ділення на нуль у калібрувальній формулі драйвера. Такій
          вибірці не місце ні в статистиці, ні в передісторії — але мовчати про
          неї не можна: непрацездатний давач це аварія, і про неї треба в ефір. */
    if (!isfinite(raw_sample)) {
        out.action         = DECISION_ANOMALY_ALARM;
        out.sensor_fault   = true;
        out.running_mean   = welford_mean(&dev->stats);
        out.running_stddev = welford_stddev(&dev->stats);
        out.z_score        = 0.0f;
        dev->last_heartbeat_ms = now_ms;
        return out;
    }

    /* 1. Передісторія пишеться ЗАВЖДИ, ще до всіх рішень: саме заради
          викинутих вибірок вона й існує. */
    ring_buffer_push(&dev->snapshot, raw_sample);

    /* 2. Оцінка викиду. Доки не набралося EDGE_MIN_TRAINING_SAMPLES, оцінка
          дисперсії ще сміттєва, і будь-який поріг по ній дав би хибні тривоги
          на перших секундах після ввімкнення. */
    bool  is_anomaly = false;
    float z = 0.0f;
    if (welford_count(&dev->stats) >= EDGE_MIN_TRAINING_SAMPLES) {
        z = welford_zscore(&dev->stats, raw_sample);
        is_anomaly = (z > EDGE_Z_THRESHOLD);
    }

    /* 3. Модель норми вчиться лише на нормі. Пустити викиди в акумулятор —
          означає роздути сигму серією аварійних коливань; поріг 3 сигми
          розповзеться, і наступний справжній дефект пройде як норма. */
    if (!is_anomaly) {
        welford_update(&dev->stats, raw_sample);
    }

    out.running_mean   = welford_mean(&dev->stats);
    out.running_stddev = welford_stddev(&dev->stats);
    out.z_score        = z;

    if (is_anomaly) {
        out.action = DECISION_ANOMALY_ALARM;
        dev->last_tx_value     = raw_sample;
        dev->last_heartbeat_ms = now_ms;
        dev->has_tx            = true;
        return out;
    }

    /* 4. Дельта-стиснення. Різниця з ОСТАННІМ ПЕРЕДАНИМ значенням, а не з
          попередньою вибіркою: інакше повільний дрейф ніколи не перетнув би
          поріг і хмара роками бачила б перше ж значення.
          Віднімання міток часу беззнакове й тому переживає обгортання
          лічильника мілісекунд на 49.7 добі — різниця лишається правильною. */
    const bool first_ever    = !dev->has_tx;
    const float delta        = fabsf(raw_sample - dev->last_tx_value);
    const bool  moved        = (delta >= EDGE_DEADBAND);
    const bool  heartbeat_due =
        (uint32_t)(now_ms - dev->last_heartbeat_ms) >= EDGE_HEARTBEAT_INTERVAL_MS;

    if (first_ever || moved || heartbeat_due) {
        out.action = DECISION_HEARTBEAT;
        dev->last_tx_value     = raw_sample;
        dev->last_heartbeat_ms = now_ms;
        dev->has_tx            = true;
    } else {
        out.action = DECISION_DISCARD;
    }

    return out;
}
