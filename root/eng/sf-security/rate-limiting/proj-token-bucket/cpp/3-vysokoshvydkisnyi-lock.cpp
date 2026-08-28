#include <atomic>
#include <chrono>
#include <cstdint>
#include <algorithm>

class LockFreeGcraLimiter {
public:
    LockFreeGcraLimiter(uint64_t rate_per_sec, uint64_t burst_capacity)
        : emission_interval_ns_(1'000'000'000ULL / rate_per_sec),
          burst_tolerance_ns_((burst_capacity - 1) * emission_interval_ns_),
          tat_ns_(0) {}

    bool try_acquire() {
        uint64_t now = current_time_ns();
        uint64_t current_tat = tat_ns_.load(std::memory_order_relaxed);

        while (true) {
            // Перевірка, чи не перевищує запит допустимий ліміт сплеску
            if (current_tat > now + burst_tolerance_ns_) {
                return false;
            }

            uint64_t base = std::max(now, current_tat);
            uint64_t next_tat = base + emission_interval_ns_;

            if (tat_ns_.compare_exchange_weak(
                    current_tat,
                    next_tat,
                    std::memory_order_acq_rel,
                    std::memory_order_relaxed)) {
                return true;
            }
        }
    }

private:
    static uint64_t current_time_ns() {
        auto now = std::chrono::steady_clock::now().time_since_epoch();
        return std::chrono::duration_cast<std::chrono::nanoseconds>(now).count();
    }

    const uint64_t emission_interval_ns_;
    const uint64_t burst_tolerance_ns_;
    std::atomic<uint64_t> tat_ns_;
};
