#include <chrono>
#include <mutex>
#include <algorithm>
#include <cstdint>

class TokenBucket {
public:
    TokenBucket(double capacity, double refill_rate_per_sec)
        : capacity_(capacity),
          tokens_(capacity),
          refill_rate_(refill_rate_per_sec),
          last_refill_tp_(std::chrono::steady_clock::now()) {}

    bool try_consume(double tokens_to_consume = 1.0) {
        std::lock_guard<std::mutex> lock(mutex_);

        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_refill_tp_;
        last_refill_tp_ = now;

        // Поповнення токенів
        tokens_ = std::min(capacity_, tokens_ + elapsed.count() * refill_rate_);

        if (tokens_ >= tokens_to_consume) {
            tokens_ -= tokens_to_consume;
            return true;
        }

        return false;
    }

private:
    const double capacity_;
    const double refill_rate_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_tp_;
    std::mutex mutex_;
};
