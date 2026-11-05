#include <atomic>
#include <vector>
#include <chrono>
#include <cstdint>

class SlidingWindowCounter {
private:
    struct alignas(64) Bucket {
        std::atomic<std::int64_t> timestamp{-1};
        std::atomic<std::int64_t> counter{0};
    };

    const std::int64_t window_size;
    std::vector<Bucket> buckets;

    std::int64_t get_current_sec() const {
        using namespace std::chrono;
        return duration_cast<seconds>(system_clock::now().time_since_epoch()).count();
    }

public:
    explicit SlidingWindowCounter(std::int64_t window_seconds = 60)
        : window_size(window_seconds), buckets(window_seconds) {}

    void increment() {
        std::int64_t now_sec = get_current_sec();
        size_t index = static_cast<size_t>(now_sec % window_size);
        Bucket& bucket = buckets[index];

        std::int64_t bucket_time = bucket.timestamp.load(std::memory_order_relaxed);
        if (bucket_time != now_sec) {
            if (bucket.timestamp.compare_exchange_strong(bucket_time, now_sec,
                                                          std::memory_order_acq_rel)) {
                bucket.counter.store(0, std::memory_order_relaxed);
            }
        }
        bucket.counter.fetch_add(1, std::memory_order_relaxed);
    }

    std::int64_t get_sum() const {
        std::int64_t now_sec = get_current_sec();
        std::int64_t total_sum = 0;

        for (const auto& bucket : buckets) {
            std::int64_t bucket_time = bucket.timestamp.load(std::memory_order_acquire);
            if (now_sec - bucket_time < window_size && bucket_time > 0) {
                total_sum += bucket.counter.load(std::memory_order_relaxed);
            }
        }
        return total_sum;
    }
};
