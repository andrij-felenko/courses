#include <vector>
#include <cstdint>
#include <algorithm>

struct CppTelemetryRecord {
    std::uint32_t sensor_id;
    std::uint64_t timestamp_ns;
    float         raw_value;
    std::uint8_t  flags;
};

std::size_t process_telemetry_cpp_raii(std::vector<CppTelemetryRecord>& records, float scale) {
    // Еквівалентний RAII-безпечний варіант C++ без сирих вказівників
    auto write_it = records.begin();
    for (const auto& rec : records) {
        if (rec.flags & 1) {
            *write_it = rec;
            write_it->raw_value *= scale;
            ++write_it;
        }
    }
    records.erase(write_it, records.end());

    std::sort(records.begin(), records.end(), [](const CppTelemetryRecord& a, const CppTelemetryRecord& b) {
        if (a.sensor_id != b.sensor_id) return a.sensor_id < b.sensor_id;
        return a.timestamp_ns < b.timestamp_ns;
    });

    return records.size();
}
