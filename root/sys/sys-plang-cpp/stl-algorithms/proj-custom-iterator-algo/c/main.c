#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t sensor_id;
    uint64_t timestamp_ns;
    float    raw_value;
    uint8_t  flags;
} CTelemetryRecord;

// Компаратор для qsort: порівняння спочатку за sensor_id, потім за timestamp_ns
int compare_telemetry(const void* a, const void* b) {
    const CTelemetryRecord* rec_a = (const CTelemetryRecord*)a;
    const CTelemetryRecord* rec_b = (const CTelemetryRecord*)b;

    if (rec_a->sensor_id != rec_b->sensor_id) {
        return (rec_a->sensor_id < rec_b->sensor_id) ? -1 : 1;
    }
    if (rec_a->timestamp_ns != rec_b->timestamp_ns) {
        return (rec_a->timestamp_ns < rec_b->timestamp_ns) ? -1 : 1;
    }
    return 0;
}

size_t process_telemetry_c(CTelemetryRecord* records, size_t count, float scale) {
    // 1. Ручна фільтрація та калібрування в один прохід
    size_t valid_count = 0;
    for (size_t i = 0; i < count; ++i) {
        if ((records[i].flags & 1) != 0) { // Перевірка прапорця FLAG_VALID
            records[valid_count] = records[i];
            records[valid_count].raw_value *= scale;
            valid_count++;
        }
    }

    // 2. Сортування через qsort (непрямі виклики компаратора через вказівник)
    qsort(records, valid_count, sizeof(CTelemetryRecord), compare_telemetry);

    return valid_count;
}
