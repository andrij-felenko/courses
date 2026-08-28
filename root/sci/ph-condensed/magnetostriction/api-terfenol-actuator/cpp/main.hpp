#pragma once
#include <cstdint>
#include <expected>
#include <string_view>
#include <span>

namespace gmm {

enum class Error {
    Success = 0,
    InvalidParam = -1,
    NotConnected = -2,
    Overtemperature = -3,
    Overcurrent = -4,
    LvdtFailure = -5,
    Timeout = -6
};

struct Config {
    std::uint32_t can_node_id{1};
    std::uint32_t position_limit_nm{100000};
    std::uint16_t max_current_ma{6000};
    std::uint16_t temp_limit_ddeg{800};
};

struct Telemetry {
    std::int32_t actual_position_nm{0};
    std::int16_t coil_current_ma{0};
    std::int16_t temperature_ddeg{0};
    std::uint32_t status_flags{0};
    bool is_enabled{false};
};

class Actuator {
public:
    static std::expected<Actuator, Error> connect(const Config& config) noexcept;
    
    std::expected<void, Error> set_enabled(bool enable) noexcept;
    std::expected<void, Error> set_position(std::int32_t position_nm) noexcept;
    std::expected<void, Error> set_current_open_loop(std::int16_t current_ma) noexcept;
    [[nodiscard]] std::expected<Telemetry, Error> get_telemetry() const noexcept;
    std::expected<void, Error> reset_fault() noexcept;
};

} // namespace gmm
