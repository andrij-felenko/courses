#include <cstdint>
#include <optional>

struct GapConnParams {
    uint16_t interval_min{24};  // 30.0 мс (24 * 1.25)
    uint16_t interval_max{40};  // 50.0 мс (40 * 1.25)
    uint16_t latency{4};        // Пропуск 4 подій
    uint16_t timeout{300};      // 3000 мс (300 * 10)

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        if (interval_min < 6 || interval_min > 3200) return false;
        if (interval_max < interval_min || interval_max > 3200) return false;
        if (latency > 499) return false;
        if (timeout < 10 || timeout > 3200) return false;

        // Supervision_Timeout * 10 мс > (1 + Latency) * 2 * (Interval_Max * 1.25 мс)
        // Timeout * 4 > (1 + Latency) * Interval_Max
        const auto effective_units = static_cast<uint32_t>(1 + latency) * interval_max;
        const auto timeout_scaled  = static_cast<uint32_t>(timeout) * 4;

        return timeout_scaled > effective_units;
    }

    [[nodiscard]] constexpr double effective_max_latency_ms() const noexcept {
        return (1 + latency) * (interval_max * 1.25);
    }
};
