#pragma once
#include <cstdint>
#include <algorithm>
#include <random>
#include <chrono>

namespace fleet {

class BackoffManager {
public:
    using Milliseconds = std::chrono::milliseconds;

    constexpr BackoffManager(Milliseconds base, Milliseconds max) noexcept
        : base_(base), max_(max), current_(base) {}

    template <typename UniformRng>
    Milliseconds next_delay(UniformRng& rng) noexcept {
        const auto high = std::min(max_, current_ * 3);
        if (high <= base_) {
            current_ = base_;
            return base_;
        }
        std::uniform_int_distribution<uint32_t> dist(
            static_cast<uint32_t>(base_.count()),
            static_cast<uint32_t>(high.count())
        );
        current_ = Milliseconds(dist(rng));
        return current_;
    }

    void reset() noexcept {
        current_ = base_;
    }

    static std::chrono::seconds calculate_initial_jitter(
        std::chrono::seconds window, uint32_t raw_random) noexcept {
        if (window.count() == 0) return std::chrono::seconds(0);
        return std::chrono::seconds(raw_random % window.count());
    }

private:
    Milliseconds base_;
    Milliseconds max_;
    Milliseconds current_;
};

} // namespace fleet
