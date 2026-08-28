#include <mutex>
#include <cstdint>

struct MetricsSnapshot {
    uint64_t total_bytes{0};
    uint64_t error_count{0};
};

class SynchronizedMetrics {
public:
    void record(int status_code, uint64_t bytes) {
        std::lock_guard<std::mutex> guard(mutex_);
        total_bytes_ += bytes;
        if (status_code >= 400) {
            ++error_count_;
        }
    }

    [[nodiscard]] MetricsSnapshot get_snapshot() const {
        std::lock_guard<std::mutex> guard(mutex_);
        return {total_bytes_, error_count_};
    }

private:
    mutable std::mutex mutex_{};
    uint64_t total_bytes_{0};
    uint64_t error_count_{0};
};
