#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint32_t total_incoming;
    uint32_t suppressed_dedup;
    uint32_t suppressed_conflated;
    uint32_t suppressed_out_of_order;
    uint32_t dispatched_count;
    uint32_t max_buffer_latency_ms;
} conflation_telemetry_raw_t;

typedef struct {
    float suppression_rate;
    float dedup_ratio;
    float conflated_ratio;
    uint32_t total_suppressed;
    uint32_t dispatched_count;
    uint32_t max_buffer_latency_ms;
} conflation_telemetry_stats_t;

void conflation_telemetry_init(conflation_telemetry_raw_t *raw) {
    memset(raw, 0, sizeof(conflation_telemetry_raw_t));
}

void conflation_telemetry_record_incoming(conflation_telemetry_raw_t *raw) {
    raw->total_incoming++;
}

void conflation_telemetry_record_dedup(conflation_telemetry_raw_t *raw) {
    raw->suppressed_dedup++;
}

void conflation_telemetry_record_conflated(conflation_telemetry_raw_t *raw) {
    raw->suppressed_conflated++;
}

void conflation_telemetry_record_out_of_order(conflation_telemetry_raw_t *raw) {
    raw->suppressed_out_of_order++;
}

void conflation_telemetry_record_dispatch(conflation_telemetry_raw_t *raw, uint32_t latency_ms) {
    raw->dispatched_count++;
    if (latency_ms > raw->max_buffer_latency_ms) {
        raw->max_buffer_latency_ms = latency_ms;
    }
}

bool conflation_telemetry_calculate_stats(const conflation_telemetry_raw_t *raw, conflation_telemetry_stats_t *stats) {
    if (!raw || !stats) {
        return false;
    }

    stats->total_suppressed = raw->suppressed_dedup + raw->suppressed_conflated + raw->suppressed_out_of_order;
    stats->dispatched_count = raw->dispatched_count;
    stats->max_buffer_latency_ms = raw->max_buffer_latency_ms;

    if (raw->total_incoming == 0) {
        stats->suppression_rate = 0.0f;
        stats->dedup_ratio = 0.0f;
        stats->conflated_ratio = 0.0f;
        return true;
    }

    stats->suppression_rate = (float)stats->total_suppressed / (float)raw->total_incoming;
    stats->dedup_ratio = (float)raw->suppressed_dedup / (float)raw->total_incoming;
    stats->conflated_ratio = (float)raw->suppressed_conflated / (float)raw->total_incoming;

    return true;
}
