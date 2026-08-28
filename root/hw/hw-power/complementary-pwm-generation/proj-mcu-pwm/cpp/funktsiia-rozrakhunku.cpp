#include <cstdint>
#include <algorithm>

namespace power_control {

class Stm32DeadTimeCalculator {
public:
    static constexpr uint8_t calculate_dtg(uint32_t dead_time_ns, uint32_t timer_freq_hz) noexcept {
        const uint64_t t_dts_ps = 1'000'000'000'000ULL / timer_freq_hz;
        const uint32_t ticks = static_cast<uint32_t>((dead_time_ns * 1'000ULL + t_dts_ps / 2) / t_dts_ps);

        if (ticks <= 127) {
            return static_cast<uint8_t>(ticks);
        }
        if (ticks <= 254) {
            const uint32_t raw = std::clamp((ticks / 2) - 64, 0u, 0x3Fu);
            return static_cast<uint8_t>(0x80 | raw);
        }
        if (ticks <= 504) {
            const uint32_t raw = std::clamp((ticks / 8) - 32, 0u, 0x1Fu);
            return static_cast<uint8_t>(0xC0 | raw);
        }
        if (ticks <= 1008) {
            const uint32_t raw = std::clamp((ticks / 16) - 32, 0u, 0x1Fu);
            return static_cast<uint8_t>(0xE0 | raw);
        }
        return 0xFF;
    }
};

} // namespace power_control
