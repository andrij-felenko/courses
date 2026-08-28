/* src/collector.h — C-інтерфейс утиліти для сумісності з низькорівневими модулями */
#ifndef COLLECTOR_H
#define COLLECTOR_H

#include <stdint.h>

struct CTelemetryRecord {
    const char* sensor_id;
    double temperature;
    uint32_t pressure_hpa;
    uint64_t timestamp_ms;
};

#endif /* COLLECTOR_H */
