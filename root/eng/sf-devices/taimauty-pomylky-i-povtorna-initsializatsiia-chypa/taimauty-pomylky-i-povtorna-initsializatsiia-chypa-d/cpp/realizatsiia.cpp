#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>
#include "stm32f4xx.h"

enum class BusError : uint8_t {
    Timeout,
    Nack,
    BusStuck,
    ArbitrationLost,
    Overrun,
    CrcMismatch
};

class DwtTimeout {
public:
    explicit DwtTimeout(std::chrono::microseconds duration, uint32_t cpu_freq_hz = SystemCoreClock) noexcept
        : start_cycles_{DWT->CYCCNT},
          timeout_cycles_{static_cast<uint32_t>((static_cast<uint64_t>(duration.count()) * cpu_freq_hz) / 1'000'000ULL)} {}

    [[nodiscard]] bool is_expired() const noexcept {
        const uint32_t elapsed = DWT->CYCCNT - start_cycles_;
        return elapsed >= timeout_cycles_;
    }

    template <typename Predicate>
        requires std::predicate<Predicate>
    [[nodiscard]] std::expected<void, BusError> wait_until(Predicate&& pred) const noexcept {
        while (!pred()) {
            if (is_expired()) {
                return std::unexpected(BusError::Timeout);
            }
        }
        return {};
    }

private:
    uint32_t start_cycles_;
    uint32_t timeout_cycles_;
};

// Приклад використання для безпечного опитування статусного регістра
std::expected<void, BusError> i2c_wait_flag(volatile uint32_t* reg, uint32_t mask, bool wait_set, std::chrono::microseconds timeout) noexcept {
    const DwtTimeout timer{timeout};
    return timer.wait_until([reg, mask, wait_set] {
        const bool is_set = (*reg & mask) != 0;
        return is_set == wait_set;
    });
}
