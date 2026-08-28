// TimeGuard.hpp - Idiomatic C++20 precision monotonic time and deadline wrapper
#pragma once

#include <chrono>
#include <thread>
#include <concepts>
#include <algorithm>

namespace timing {

using namespace std::chrono_literals;

class MonotonicClock {
public:
    using clock_type = std::chrono::steady_clock;
    using time_point = clock_type::time_point;
    using duration   = clock_type::duration;

    static time_point now() noexcept {
        return clock_type::now();
    }
};

class Deadline {
public:
    explicit Deadline(std::chrono::nanoseconds timeout) noexcept
        : start_(MonotonicClock::now())
        , timeout_(timeout) {}

    template <typename Rep, typename Period>
    explicit Deadline(const std::chrono::duration<Rep, Period>& timeout) noexcept
        : Deadline(std::chrono::duration_cast<std::chrono::nanoseconds>(timeout)) {}

    [[nodiscard]] bool is_expired() const noexcept {
        return remaining_duration() == std::chrono::nanoseconds::zero();
    }

    [[nodiscard]] std::chrono::nanoseconds remaining_duration() const noexcept {
        const auto now = MonotonicClock::now();
        const auto elapsed = (now >= start_) ? (now - start_) : MonotonicClock::duration::zero();
        if (elapsed >= timeout_) {
            return std::chrono::nanoseconds::zero();
        }
        return std::chrono::duration_cast<std::chrono::nanoseconds>(timeout_ - elapsed);
    }

    template <typename DurationType = std::chrono::milliseconds>
    [[nodiscard]] typename DurationType::rep remaining() const noexcept {
        return std::chrono::duration_cast<DurationType>(remaining_duration()).count();
    }

    void reset() noexcept {
        start_ = MonotonicClock::now();
    }

private:
    MonotonicClock::time_point start_;
    std::chrono::nanoseconds timeout_;
};

class PeriodicTicker {
public:
    explicit PeriodicTicker(std::chrono::nanoseconds period) noexcept
        : period_(period)
        , next_tick_(MonotonicClock::now() + period_) {}

    template <typename Rep, typename Period>
    explicit PeriodicTicker(const std::chrono::duration<Rep, Period>& period) noexcept
        : PeriodicTicker(std::chrono::duration_cast<std::chrono::nanoseconds>(period)) {}

    [[nodiscard]] bool poll() noexcept {
        const auto now = MonotonicClock::now();
        if (now >= next_tick_) {
            next_tick_ += period_;
            if (now >= next_tick_) {
                next_tick_ = now + period_; // захист від лавини після провисання
            }
            return true;
        }
        return false;
    }

    void sleep_until_next() {
        const auto now = MonotonicClock::now();
        if (next_tick_ > now) {
            std::this_thread::sleep_until(next_tick_);
        }
        next_tick_ += period_;
    }

private:
    std::chrono::nanoseconds period_;
    MonotonicClock::time_point next_tick_;
};

} // namespace timing
