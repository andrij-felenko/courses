// Конфігурація часових параметрів I2C за специфікацією NXP UM10204 (C++20)
#pragma once
#include <cstdint>
#include <chrono>
#include <optional>
#include <string_view>

namespace i2c::timing {

using namespace std::chrono_literals;

enum class SpeedMode : uint8_t {
    Standard100k,
    Fast400k,
    FastPlus1M,
    HighSpeed3M4
};

struct TimingSpec {
    uint32_t scl_frequency_hz;
    std::chrono::nanoseconds t_low;
    std::chrono::nanoseconds t_high;
    std::chrono::nanoseconds t_su_dat;
    std::chrono::nanoseconds t_hd_dat;
    std::chrono::nanoseconds t_su_sta;
    std::chrono::nanoseconds t_hd_sta;
    std::chrono::nanoseconds t_su_sto;
    std::chrono::nanoseconds t_buf;
    std::chrono::nanoseconds t_r_max;
    std::chrono::nanoseconds t_f_max;
    uint8_t spike_filter_cycles;

    [[nodiscard]] constexpr std::chrono::nanoseconds min_period() const noexcept {
        return t_low + t_high + t_r_max + t_f_max;
    }

    [[nodiscard]] constexpr bool is_compliant() const noexcept {
        return (t_su_dat >= 50ns) && (t_low >= 500ns) && (t_high >= 260ns);
    }
};

constexpr TimingSpec standard_mode{
    .scl_frequency_hz = 100'000,
    .t_low            = 4700ns,
    .t_high           = 4000ns,
    .t_su_dat         = 250ns,
    .t_hd_dat         = 300ns,
    .t_su_sta         = 4700ns,
    .t_hd_sta         = 4000ns,
    .t_su_sto         = 4000ns,
    .t_buf            = 4700ns,
    .t_r_max          = 1000ns,
    .t_f_max          = 300ns,
    .spike_filter_cycles = 0
};

constexpr TimingSpec fast_mode{
    .scl_frequency_hz = 400'000,
    .t_low            = 1300ns,
    .t_high           = 600ns,
    .t_su_dat         = 100ns,
    .t_hd_dat         = 300ns,
    .t_su_sta         = 600ns,
    .t_hd_sta         = 600ns,
    .t_su_sto         = 600ns,
    .t_buf            = 1300ns,
    .t_r_max          = 300ns,
    .t_f_max          = 300ns,
    .spike_filter_cycles = 2
};

constexpr TimingSpec fast_mode_plus{
    .scl_frequency_hz = 1'000'000,
    .t_low            = 500ns,
    .t_high           = 260ns,
    .t_su_dat         = 50ns,
    .t_hd_dat         = 0ns,
    .t_su_sta         = 260ns,
    .t_hd_sta         = 260ns,
    .t_su_sto         = 260ns,
    .t_buf            = 500ns,
    .t_r_max          = 120ns,
    .t_f_max          = 120ns,
    .spike_filter_cycles = 1
};

[[nodiscard]] constexpr const TimingSpec& get_spec(SpeedMode mode) noexcept {
    switch (mode) {
        case SpeedMode::Standard100k: return standard_mode;
        case SpeedMode::Fast400k:     return fast_mode;
        case SpeedMode::FastPlus1M:   return fast_mode_plus;
        case SpeedMode::HighSpeed3M4: return fast_mode_plus;
    }
    return standard_mode;
}

} // namespace i2c::timing
