#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define SNAPSHOT_BUFFER_SIZE 32
#define DEFAULT_Z_THRESHOLD  3.0f
#define DEFAULT_DEADBAND     0.5f

/**
 * @brief Структура потокової статистики за алгоритмом Велфорда.
 */
typedef struct {
    uint32_t count;
    float mean;
    float m2;
} welford_stat_t;

void welford_init(welford_stat_t *stat) {
    if (!stat) return;
    stat->count = 0;
    stat->mean = 0.0f;
    stat->m2 = 0.0f;
}

void welford_update(welford_stat_t *stat, float x) {
    if (!stat) return;
    stat->count++;
    float delta = x - stat->mean;
    stat->mean += delta / (float)stat->count;
    float delta2 = x - stat->mean;
    stat->m2 += delta * delta2;
}

float welford_variance(const welford_stat_t *stat) {
    if (!stat || stat->count < 2) return 0.0f;
    return stat->m2 / (float)(stat->count - 1);
}

float welford_stddev(const welford_stat_t *stat) {
    return sqrtf(welford_variance(stat));
}

float welford_zscore(const welford_stat_t *stat, float x) {
    float s = welford_stddev(stat);
    if (s < 1e-6f) return 0.0f;
    return fabsf(x - stat->mean) / s;
}

/**
 * @brief Кільцевий буфер для збереження передісторії сигналу (Snapshot).
 */
typedef struct {
    float buffer[SNAPSHOT_BUFFER_SIZE];
    uint32_t head;
    uint32_t count;
} ring_buffer_t;

void ring_init(ring_buffer_t *rb) {
    if (!rb) return;
    rb->head = 0;
    rb->count = 0;
    memset(rb->buffer, 0, sizeof(rb->buffer));
}

void ring_push(ring_buffer_t *rb, float sample) {
    if (!rb) return;
    rb->buffer[rb->head] = sample;
    rb->head = (rb->head + 1) % SNAPSHOT_BUFFER_SIZE;
    if (rb->count < SNAPSHOT_BUFFER_SIZE) {
        rb->count++;
    }
}

void ring_copy_linear(const ring_buffer_t *rb, float *dest, uint32_t max_len) {
    if (!rb || !dest || max_len == 0) return;
    uint32_t to_copy = (rb->count < max_len) ? rb->count : max_len;
    uint32_t start = (rb->head + SNAPSHOT_BUFFER_SIZE - rb->count) % SNAPSHOT_BUFFER_SIZE;
    for (uint32_t i = 0; i < to_copy; ++i) {
        dest[i] = rb->buffer[(start + i) % SNAPSHOT_BUFFER_SIZE];
    }
}

/**
 * @brief Тип результуючої дії для диспетчера телеметрії.
 */
typedef enum {
    DECISION_DISCARD = 0,    /* Значення в межах зони нечутливості */
    DECISION_HEARTBEAT,      /* Періодичне зведення норми */
    DECISION_ANOMALY_ALARM   /* Виявлено викид, термінова відправка */
} telemetry_action_t;

typedef struct {
    telemetry_action_t action;
    float value;
    float running_mean;
    float running_stddev;
    float z_score;
    uint32_t timestamp_ms;
} telemetry_packet_t;

/**
 * @brief Контекст бортового процесора обробки сигналу.
 */
typedef struct {
    welford_stat_t stats;
    ring_buffer_t snapshot_ring;
    float last_transmitted_value;
    uint32_t last_heartbeat_ms;
    uint32_t heartbeat_interval_ms;
    float deadband;
    float z_threshold;
    uint32_t min_training_samples;
} edge_detector_t;

void edge_detector_init(edge_detector_t *dev,
                        float deadband,
                        float z_threshold,
                        uint32_t heartbeat_interval_ms) {
    if (!dev) return;
    welford_init(&dev->stats);
    ring_init(&dev->snapshot_ring);
    dev->last_transmitted_value = 0.0f;
    dev->last_heartbeat_ms = 0;
    dev->heartbeat_interval_ms = heartbeat_interval_ms;
    dev->deadband = (deadband > 0.0f) ? deadband : DEFAULT_DEADBAND;
    dev->z_threshold = (z_threshold > 0.0f) ? z_threshold : DEFAULT_Z_THRESHOLD;
    dev->min_training_samples = 30; /* мінімум вибірок для адаптації дисперсії */
}

telemetry_packet_t edge_detector_process_sample(edge_detector_t *dev,
                                               float raw_sample,
                                               uint32_t current_time_ms) {
    telemetry_packet_t out;
    memset(&out, 0, sizeof(out));
    out.value = raw_sample;
    out.timestamp_ms = current_time_ms;

    if (!dev) {
        out.action = DECISION_DISCARD;
        return out;
    }

    /* 1. Збереження вибірки в буфер передісторії */
    ring_push(&dev->snapshot_ring, raw_sample);

    /* 2. Перевірка на аномалію, якщо модель накопичила базову вибірку */
    bool is_anomaly = false;
    float z = 0.0f;
    if (dev->stats.count >= dev->min_training_samples) {
        z = welford_zscore(&dev->stats, raw_sample);
        if (z > dev->z_threshold) {
            is_anomaly = true;
        }
    }

    /* 3. Оновлення моделі норми (аномалії ізолюються від статистики) */
    if (!is_anomaly) {
        welford_update(&dev->stats, raw_sample);
    }

    out.running_mean = dev->stats.mean;
    out.running_stddev = welford_stddev(&dev->stats);
    out.z_score = z;

    /* 4. Прийняття рішення про відправку в ефір */
    if (is_anomaly) {
        out.action = DECISION_ANOMALY_ALARM;
        dev->last_transmitted_value = raw_sample;
        dev->last_heartbeat_ms = current_time_ms;
        return out;
    }

    /* Перевірка порогу зони нечутливості Deadband */
    float delta = fabsf(raw_sample - dev->last_transmitted_value);
    bool heartbeat_due = (current_time_ms - dev->last_heartbeat_ms) >= dev->heartbeat_interval_ms;

    if (delta >= dev->deadband || heartbeat_due) {
        out.action = DECISION_HEARTBEAT;
        dev->last_transmitted_value = raw_sample;
        dev->last_heartbeat_ms = current_time_ms;
    } else {
        out.action = DECISION_DISCARD;
    }

    return out;
}
