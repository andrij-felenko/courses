#ifndef EDGE_DETECTOR_H
#define EDGE_DETECTOR_H

#include <stdbool.h>
#include <stdint.h>

#include "ring_buffer.h"
#include "welford.h"

/*
 * Пороги модуля — компіляційні сталі, не поля структури.
 * Пристрій має один режим роботи; чотири налаштовуваних поля коштували б
 * 16 байт BSS на кожен екземпляр і жодного разу за життя не змінилися б.
 */
#define EDGE_DEADBAND               0.5f     /* зона нечутливості, одиниці сигналу */
#define EDGE_Z_THRESHOLD            3.0f     /* поріг викиду в сигмах */
#define EDGE_MIN_TRAINING_SAMPLES   30u      /* доки менше — тривог не буває */
#define EDGE_HEARTBEAT_INTERVAL_MS  60000u   /* «я живий» раз на хвилину */

typedef enum {
    DECISION_DISCARD       = 0,  /* у межах зони нечутливості — в ефір нічого */
    DECISION_HEARTBEAT     = 1,  /* планове зведення норми або зсув понад deadband */
    DECISION_ANOMALY_ALARM = 2   /* викид або відмова давача — термінова відправка */
} telemetry_action_t;

typedef struct {
    telemetry_action_t action;
    float              value;
    float              running_mean;
    float              running_stddev;
    float              z_score;
    uint32_t           timestamp_ms;
    bool               sensor_fault;  /* вибірка не є скінченним числом */
} telemetry_report_t;

typedef struct {
    welford_t     stats;
    ring_buffer_t snapshot;
    float         last_tx_value;
    uint32_t      last_heartbeat_ms;
    bool          has_tx;             /* чи була взагалі хоч одна передача */
} edge_detector_t;

void edge_detector_init(edge_detector_t *dev, uint32_t now_ms);

/* Скидає накопичену статистику й передісторію. Диспетчер кличе це раз на добу:
   так модель відпускає повільний дрейф робочої точки (сезонний нагрів). */
void edge_detector_reset(edge_detector_t *dev, uint32_t now_ms);

/* Уся робота на вибірку: O(1) інструкцій, нуль звертань до купи. */
telemetry_report_t edge_detector_process(edge_detector_t *dev,
                                         float raw_sample,
                                         uint32_t now_ms);

/* Лінійний знімок передісторії для аварійного пакета. */
uint32_t edge_detector_snapshot(const edge_detector_t *dev,
                                float *dest,
                                uint32_t dest_len);

#endif /* EDGE_DETECTOR_H */
