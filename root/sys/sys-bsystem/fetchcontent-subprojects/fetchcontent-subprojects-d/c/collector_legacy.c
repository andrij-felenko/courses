/* src/collector_legacy.c — C-реалізація форматування для базового тестового стенду */
#include "collector.h"
#include <stdio.h>
#include <stdlib.h>

char* format_c_telemetry_report(const struct CTelemetryRecord* rec) {
    char* buffer = (char*)malloc(256);
    if (!buffer) return NULL;
    snprintf(buffer, 256, "[Timestamp: %llu] Sensor '%s': Temp = %.2f C, Pressure = %u hPa",
             (unsigned long long)rec->timestamp_ms, rec->sensor_id, rec->temperature, rec->pressure_hpa);
    return buffer;
}
