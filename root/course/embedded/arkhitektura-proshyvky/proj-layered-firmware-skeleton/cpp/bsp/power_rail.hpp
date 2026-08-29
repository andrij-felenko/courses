// bsp/power_rail.hpp — ключ MOSFET, яким плата знеструмлює лінію давачів.
// Знає про плату (полярність ключа, час розряду ємностей), але не про чип.
#pragma once

#include <chrono>
#include <cstdint>

#include "hal/clock.hpp"
#include "hal/hal_gpio.hpp"

namespace bsp {

class PowerRail {
public:
    PowerRail(hal::IGpioPin& enable, hal::IClock& clock, hal::Level active_level,
              std::chrono::milliseconds off_hold, std::chrono::milliseconds startup) noexcept
        : enable_(enable),
          clock_(clock),
          active_level_(active_level),
          off_hold_(off_hold),
          startup_(startup)
    {
    }

    bool on();
    bool off();

    // Вимкнути, витримати, увімкнути, витримати старт. Саме цей виклик рятує шину,
    // коли давач притиснув SDA до землі й не відпускає.
    bool power_cycle();

    std::uint32_t cycles() const noexcept { return cycles_; }

private:
    hal::IGpioPin& enable_;
    hal::IClock& clock_;
    hal::Level active_level_;
    std::chrono::milliseconds off_hold_;
    std::chrono::milliseconds startup_;
    std::uint32_t cycles_{0};
};

}  // namespace bsp
