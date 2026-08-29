// stm32_board.hpp — цільова реалізація IBoardSupport для STM32F4.
#pragma once

#include "board.hpp"

namespace bsp {

class Stm32Board final : public IBoardSupport {
public:
    // Ставить лінії в безпечний стан і зчитує калібрування BME280.
    // Викликати ПІСЛЯ згенерованих CubeMX MX_*_Init.
    Status init() noexcept;

    Status led_set(LedId led, LedState state) noexcept override;
    Status power_domain_set(PowerDomain domain, bool enable) noexcept override;
    std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept override;
    std::expected<EnvironmentMetrics, Status> read_environment() noexcept override;
    Status enter_low_power(SleepMode mode, std::chrono::milliseconds timeout) noexcept override;
    void delay(std::chrono::milliseconds duration) noexcept override;
    [[nodiscard]] std::chrono::milliseconds uptime() const noexcept override;

private:
    std::uint16_t dig_t1_{0};
    std::int16_t dig_t2_{0};
    std::int16_t dig_t3_{0};
    bool bme_ready_{false};
};

} // namespace bsp
