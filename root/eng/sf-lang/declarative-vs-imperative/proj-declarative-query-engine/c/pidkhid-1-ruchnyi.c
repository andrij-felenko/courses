#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t sensor_id;
    double   value;
    uint64_t timestamp;
    bool     is_valid;
} SensorRecord;

double process_imperative(const SensorRecord* records, size_t count, uint32_t target_sensor, double threshold, size_t limit) {
    double sum = 0.0;
    size_t matches = 0;

    for (size_t i = 0; i < count; ++i) {
        // Явна покрокова перевірка фільтрів
        if (!records[i].is_valid) {
            continue;
        }
        if (records[i].sensor_id != target_sensor) {
            continue;
        }
        if (records[i].value < threshold) {
            continue;
        }

        // Трансформація та мутація стану
        double calibrated = records[i].value * 1.08 + 0.5;
        sum += calibrated;
        matches++;

        // Дострокове завершення
        if (matches >= limit) {
            break;
        }
    }

    return sum;
}
