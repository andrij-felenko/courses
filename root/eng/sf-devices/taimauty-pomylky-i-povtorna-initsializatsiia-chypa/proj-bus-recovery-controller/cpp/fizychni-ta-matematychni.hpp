#ifndef DWT_TIMEOUT_HPP
#define DWT_TIMEOUT_HPP

#include <cstdint>
#include <chrono>
#include <concepts>
#include <expected>
#include "stm32f4xx.h"

enum class TimeoutStatus : uint8_t {
    Success,
    TimeoutExpired
};

class DwtTimer {
public:
    static void global_init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CYCCNT = 0;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    template <typename Rep, typename Period>
    explicit DwtTimer(std::chrono::duration<Rep, Period> duration) noexcept
        : start_cycles_{DWT->CYCCNT} {
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
        duration_cycles_ = static_cast<uint32_t>((static_cast<uint64_t>(us) * SystemCoreClock) / 1'000'000ULL);
    }

    [[nodiscard]] bool is_expired() const noexcept {
        const uint32_t elapsed = DWT->CYCCNT - start_cycles_;
        return elapsed >= duration_cycles_;
    }

    template <typename Predicate>
        requires std::predicate<Predicate>
    [[nodiscard]] std::expected<void, TimeoutStatus> wait_until(Predicate&& pred) const noexcept {
        while (!pred()) {
            if (is_expired()) {
                return std::unexpected(TimeoutStatus::TimeoutExpired);
            }
        }
        return {};
    }

    static void delay(std::chrono::microseconds us) noexcept {
        const DwtTimer timer{us};
        while (!timer.is_expired());
    }

    static void delay(std::chrono::milliseconds ms) noexcept {
        const auto count = ms.count();
        for (int64_t i = 0; i < count; ++i) {
            delay(std::chrono::microseconds{1000});
        }
    }

private:
    uint32_t start_cycles_{0};
    uint32_t duration_cycles_{0};
};

#endif // DWT_TIMEOUT_HPP
