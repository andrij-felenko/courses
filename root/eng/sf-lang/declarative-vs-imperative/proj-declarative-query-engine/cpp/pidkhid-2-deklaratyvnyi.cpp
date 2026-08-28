#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <ranges>
#include <numeric>
#include <iostream>

struct SensorRecord {
    std::uint32_t sensor_id;
    double        value;
    std::uint64_t timestamp;
    bool          is_valid;
};

// Декларативний конвеєр C++20 через std::views
double process_declarative_pipeline(std::span<const SensorRecord> records, std::uint32_t target_sensor, double threshold, std::size_t limit) {
    // 1. Опис предиката як чистої лямбди
    auto is_matching = [target_sensor, threshold](const SensorRecord& r) noexcept {
        return r.is_valid && r.sensor_id == target_sensor && r.value >= threshold;
    };

    // 2. Опис трансформації
    auto calibrate = [](const SensorRecord& r) noexcept {
        return r.value * 1.08 + 0.5;
    };

    // 3. Композиція конвеєра: декларативний ланцюг обчислення
    auto pipeline = records
        | std::views::filter(is_matching)
        | std::views::transform(calibrate)
        | std::views::take(limit);

    // 4. Агрегація (згортання результату)
    double sum = 0.0;
    for (double val : pipeline) {
        sum += val;
    }
    return sum;
}
