#include <vector>
#include <algorithm>
#include <ranges>
#include <tuple>

void process_telemetry_ranges(std::vector<TelemetryRecord>& records, float scale) {
    // 1. Пряме видалення невалідних записів у C++20
    std::erase_if(records, [](const TelemetryRecord& rec) {
        return (rec.flags & FLAG_VALID) == 0;
    });

    // 2. Калібрування значень на місці
    for (auto& rec : records) {
        rec.raw_value *= scale;
        rec.flags |= FLAG_CALIB;
    }

    // 3. Сортування за кортежною проєкцією без написання компараторів
    std::ranges::sort(records, std::less{}, [](const TelemetryRecord& rec) {
        return std::make_tuple(rec.sensor_id, rec.timestamp_ns);
    });
}

// Витягування ТОП-5 найбільших вимірювань за асимптотичний час O(N)
std::vector<TelemetryRecord> get_top_5_values(std::vector<TelemetryRecord> records) {
    std::size_t k = std::min<std::size_t>(5, records.size());
    
    // std::ranges::nth_element частково впорядковує масив за час O(N)
    std::ranges::nth_element(records, records.begin() + k, std::greater{}, &TelemetryRecord::raw_value);
    
    // Впорядковуємо лише перші 5 елементів за час O(K log K)
    std::ranges::sort(records.begin(), records.begin() + k, std::greater{}, &TelemetryRecord::raw_value);

    records.resize(k);
    return records;
}
