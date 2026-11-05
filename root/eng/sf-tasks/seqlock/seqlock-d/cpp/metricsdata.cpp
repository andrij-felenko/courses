#include <atomic>
#include <cstdint>
#include <cstring>
#include <optional>

struct MetricsData {
    std::uint64_t total_requests{0};
    std::uint64_t error_count{0};
    double processing_time_ms{0.0};
};

class SafeMetricsReader {
private:
    alignas(64) mutable std::atomic<std::uint32_t> sequence_{0};
    MetricsData data_;

public:
    // Безпечне зчитування: повертає std::optional у разі перевищення спроб
    std::optional<MetricsData> read_safe(std::uint32_t max_attempts = 1000) const noexcept {
        MetricsData snapshot;
        std::uint32_t seq1{0};
        std::uint32_t seq2{0};
        std::uint32_t attempts{0};

        do {
            seq1 = sequence_.load(std::memory_order_acquire);
            if (seq1 & 1) {
                if (++attempts > max_attempts) {
                    return std::nullopt; // Сигналізуємо про високу конкуренцію
                }
                continue;
            }

            // Тільки прямолінійне копіювання стану в локальну змінну
            std::memcpy(&snapshot, &data_, sizeof(MetricsData));

            std::atomic_thread_fence(std::memory_order_acquire);
            seq2 = sequence_.load(std::memory_order_relaxed);
        } while (seq1 != seq2);

        return snapshot;
    }
};
