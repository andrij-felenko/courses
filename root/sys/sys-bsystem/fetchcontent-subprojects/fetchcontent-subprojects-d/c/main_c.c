/* src/main_c.c — точка входу для чистого C-тесту */
#include "collector.h"
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    struct CTelemetryRecord sample = {
        .sensor_id = "ENV-PROBE-04",
        .temperature = 23.85,
        .pressure_hpa = 1013,
        .timestamp_ms = 1724000000000ULL
    };

    char* report = format_c_telemetry_report(&sample);
    if (report) {
        printf("--- C звіт ---\n%s\n", report);
        free(report);
    }
    return 0;
}
