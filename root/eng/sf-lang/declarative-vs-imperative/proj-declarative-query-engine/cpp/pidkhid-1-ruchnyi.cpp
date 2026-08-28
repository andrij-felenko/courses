#include <cstdint>
#include <cstddef>
#include <span>

struct SensorRecord {
    std::uint32_t sensor_id;
    double        value;
    std::uint64_t timestamp;
    bool          is_valid;
};

double process_imperative(std::span<const SensorRecord> records, std::uint32_t target_sensor, double threshold, std::size_t limit) {
    double sum = 0.0;
    std::size_t matches = 0;

    for (const auto& record : records) {
        if (!record.is_valid || record.sensor_id != target_sensor || record.value < threshold) {
            continue;
        }

        double calibrated = record.value * 1.08 + 0.5;
        sum += calibrated;
        ++matches;

        if (matches >= limit) {
            break;
        }
    }

    return sum;
}
