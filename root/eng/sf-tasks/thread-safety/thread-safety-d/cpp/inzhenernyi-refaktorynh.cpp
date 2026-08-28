#include <mutex>
#include <cstdint>

struct AggregatorSnapshot {
    uint64_t total_requests{0};
    uint64_t total_errors{0};
};

class RequestAggregator {
public:
    void record(bool is_error) noexcept {
        std::lock_guard<std::mutex> guard(mutex_);
        ++total_requests_;
        if (is_error) {
            ++total_errors_;
        }
    }

    [[nodiscard]] AggregatorSnapshot snapshot() const noexcept {
        std::lock_guard<std::mutex> guard(mutex_);
        return {total_requests_, total_errors_};
    }

private:
    mutable std::mutex mutex_{};
    uint64_t total_requests_{0};
    uint64_t total_errors_{0};
};
