#include <cstdint>
#include <chrono>

extern uint32_t platform_get_millis() noexcept;

class MillisTimeout {
public:
    explicit constexpr MillisTimeout(std::chrono::milliseconds timeout) noexcept
        : start_ms_(platform_get_millis()),
          timeout_ms_(static_cast<uint32_t>(timeout.count())) {}

    [[nodiscard]] bool expired() const noexcept {
        const uint32_t elapsed = platform_get_millis() - start_ms_;
        return elapsed >= timeout_ms_;
    }

private:
    uint32_t start_ms_{0};
    uint32_t timeout_ms_{0};
};
