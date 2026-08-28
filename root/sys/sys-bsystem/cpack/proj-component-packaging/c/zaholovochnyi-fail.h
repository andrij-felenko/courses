#ifndef TELEMETRY_METRICS_H
#define TELEMETRY_METRICS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint64_t uptime_seconds;
    uint64_t memory_used_bytes;
    double cpu_load_percent;
} telemetry_snapshot_t;

int telemetry_collect_metrics(telemetry_snapshot_t* out_snapshot);
void telemetry_format_json(const telemetry_snapshot_t* snapshot, char* buffer, size_t max_len);

#ifdef __cplusplus
}
#endif

#endif /* TELEMETRY_METRICS_H */
