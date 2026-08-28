#include <vector>
#include <algorithm>
#include <execution>
#include <tuple>

void process_telemetry_stl(std::vector<TelemetryRecord>& records, float scale) {
    // 1. Фізичне видалення невалідних елементів через Remove-Erase ідіому
    auto new_end = std::remove_if(records.begin(), records.end(),
        [](const TelemetryRecord& rec) {
            return (rec.flags & FLAG_VALID) == 0;
        });
    records.erase(new_end, records.end());

    // 2. Калібрування значень у векторному форматі
    std::transform(records.begin(), records.end(), records.begin(),
        [scale](TelemetryRecord rec) {
            rec.raw_value *= scale;
            rec.flags |= FLAG_CALIB;
            return rec;
        });

    // 3. Паралельне сортування (sensor_id, timestamp_ns)
    std::sort(std::execution::par, records.begin(), records.end(),
        [](const TelemetryRecord& a, const TelemetryRecord& b) {
            return std::tie(a.sensor_id, a.timestamp_ns) < std::tie(b.sensor_id, b.timestamp_ns);
        });
}
