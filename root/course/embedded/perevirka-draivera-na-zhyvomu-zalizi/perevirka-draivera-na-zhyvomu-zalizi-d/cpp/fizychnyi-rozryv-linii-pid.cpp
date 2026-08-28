// Захищена реалізація опитування шини I2C на C++ з обмеженням за часом
#include <cstdint>
#include <chrono>
#include <expected>

enum class BusError { Timeout, HardwareFault };

template <typename Predicate>
[[nodiscard]] std::expected<void, BusError> waitForCondition(
    Predicate&& pred, 
    std::chrono::microseconds timeout) noexcept 
{
    const auto start = std::chrono::steady_clock::now();
    while (!pred()) {
        if (std::chrono::duration_cast<std::chrono::microseconds>(
                std::chrono::steady_clock::now() - start) >= timeout) {
            return std::unexpected(BusError::Timeout);
        }
    }
    return {};
}
