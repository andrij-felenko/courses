#include "telemetry/metrics.h"
#include <stdio.h>
#include <time.h>

static uint64_t g_start_time = 0;

int telemetry_collect_metrics(telemetry_snapshot_t* out_snapshot) {
    if (!out_snapshot) {
        return -1;
    }
    if (g_start_time == 0) {
        g_start_time = (uint64_t)time(NULL);
    }

    out_snapshot->uptime_seconds = (uint64_t)time(NULL) - g_start_time;
    out_snapshot->memory_used_bytes = 1048576 * 42; // Фіксоване тестове значення
    out_snapshot->cpu_load_percent = 12.5;

    return 0;
}

void telemetry_format_json(const telemetry_snapshot_t* snapshot, char* buffer, size_t max_len) {
    if (!snapshot || !buffer || max_len == 0) {
        return;
    }
    snprintf(buffer, max_len,
             "{\"uptime\": %llu, \"memory_bytes\": %llu, \"cpu_load\": %.2f}\n",
             (unsigned long long)snapshot->uptime_seconds,
             (unsigned long long)snapshot->memory_used_bytes,
             snapshot->cpu_load_percent);
}
