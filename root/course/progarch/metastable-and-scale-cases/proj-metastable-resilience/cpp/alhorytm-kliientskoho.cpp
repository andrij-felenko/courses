// C++ Implementation: Exponential Backoff with Full Jitter (random header, chrono)
#include <chrono>
#include <random>
#include <algorithm>
#include <cmath>

class BackoffCalculator {
public:
    BackoffCalculator(std::chrono::milliseconds base, std::chrono::milliseconds max_delay)
        : base_(base), max_delay_(max_delay), rng_(std::random_device{}()) {}

    [[nodiscard]] std::chrono::milliseconds calculate(int attempt) {
        if (attempt <= 0) return std::chrono::milliseconds(0);

        uint64_t cap_ms = max_delay_.count();
        uint64_t base_ms = base_.count();
        uint64_t exp_delay = base_ms * (1ULL << std::min(attempt - 1, 30));
        uint64_t target_max = std::min(exp_delay, cap_ms);

        std::uniform_int_distribution<uint64_t> dist(0, target_max);
        return std::chrono::milliseconds(dist(rng_));
    }

private:
    std::chrono::milliseconds base_;
    std::chrono::milliseconds max_delay_;
    std::mt19937_64 rng_;
};
