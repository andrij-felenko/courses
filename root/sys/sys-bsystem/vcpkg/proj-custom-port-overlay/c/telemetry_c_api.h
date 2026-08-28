/* src/telemetry_c_api.h */
#ifndef TELEMETRY_C_API_H
#define TELEMETRY_C_API_H

#include <stdint.h>

struct TelemetryRecord {
    uint64_t timestamp_ns;
    uint32_t sensor_id;
    double metric_value;
};

int dispatch_telemetry_c(const struct TelemetryRecord *rec);

#endif
