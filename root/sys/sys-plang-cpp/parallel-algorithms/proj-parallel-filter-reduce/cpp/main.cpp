#include <iostream>
#include <vector>
#include <numeric>
#include <execution>
#include <algorithm>
#include <chrono>
#include <cstdint>

struct TelemetryRecord {
    uint32_t server_id;
    uint16_t status_code;
    uint32_t latency_us;
    uint32_t bytes_transferred;
};

struct AggregateMetrics {
    double total_penalty{0.0};
    uint32_t max_latency{0};

    // Строго асоціативний та комутативний оператор злиття двох метрик
    AggregateMetrics operator+(const AggregateMetrics& other) const noexcept {
        return {
            total_penalty + other.total_penalty,
            std::max(max_latency, other.max_latency)
        };
    }
};

int main() {
    constexpr size_t num_records = 10'000'000;
    std::vector<TelemetryRecord> dataset(num_records);

    // Ініціалізація тестового масиву
    for (size_t i = 0; i < num_records; ++i) {
        dataset[i] = TelemetryRecord{
            .server_id = static_cast<uint32_t>(i % 128),
            .status_code = static_cast<uint16_t>((i % 50 == 0) ? 503 : 200),
            .latency_us = static_cast<uint32_t>((i * 37) % 12000),
            .bytes_transferred = static_cast<uint32_t>((i * 101) % 65536)
        };
    }

    // Паралельний однопрохідний Map-Reduce у C++17/C++20
    const AggregateMetrics result = std::transform_reduce(
        std::execution::par_unseq,
        dataset.begin(), dataset.end(),
        AggregateMetrics{},
        std::plus<AggregateMetrics>{},
        [](const TelemetryRecord& r) noexcept -> AggregateMetrics {
            if (r.latency_us > 5000 || r.status_code >= 500) {
                double penalty = 0.0;
                if (r.latency_us > 5000) {
                    penalty += (r.latency_us - 5000) * 1.5;
                }
                penalty += static_cast<double>(r.bytes_transferred) / 1024.0;
                return AggregateMetrics{penalty, r.latency_us};
            }
            return AggregateMetrics{0.0, 0};
        }
    );

    std::cout << "[C++ std::transform_reduce] Разом штраф: " 
              << result.total_penalty 
              << " | Макс затримка: " << result.max_latency << " мкс\n";

    return 0;
}
