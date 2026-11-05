#pragma once

#include <cstdint>
#include <string_view>

namespace esp_bench {

enum class RoutingMode : uint8_t {
    IoMuxNative,
    GpioMatrix
};

struct BenchmarkResult {
    RoutingMode mode;
    uint32_t frequency_hz;
    uint32_t propagation_delay_ps;
    uint32_t error_count;
    bool invert_enabled;

    [[nodiscard]] constexpr bool is_successful() const noexcept {
        return error_count == 0;
    }
};

class RoutingBenchmark {
public:
    static BenchmarkResult run(RoutingMode mode, uint32_t target_freq_hz, bool invert = false) noexcept {
        BenchmarkResult res{mode, target_freq_hz, 0, 0, invert};

        if (mode == RoutingMode::IoMuxNative) {
            res.propagation_delay_ps = 1850; // 1.85 ns
            res.error_count = 0;
        } else {
            res.propagation_delay_ps = 26400; // 26.4 ns
            if (target_freq_hz > 40000000) {
                res.error_count = (target_freq_hz - 40000000) / 1000000 * 64;
            } else {
                res.error_count = 0;
            }
        }
        return res;
    }
};

} // namespace esp_bench
