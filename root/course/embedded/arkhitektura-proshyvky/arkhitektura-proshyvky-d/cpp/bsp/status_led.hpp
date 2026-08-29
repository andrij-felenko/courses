// bsp/status_led.hpp — індикатор стану.
// Застосунок каже «тривога», а не «увімкни вивід на 150 мілісекунд».
#pragma once

#include "hal/clock.hpp"
#include "hal/gpio.hpp"

namespace bsp {

enum class LedMode : std::uint8_t {
    Off,
    On,
    BlinkSlow,  // штатна робота
    BlinkFast   // аварія
};

class StatusLed {
public:
    explicit StatusLed(hal::OutputPin pin);

    void set_mode(LedMode mode);
    [[nodiscard]] LedMode mode() const noexcept { return mode_; }

    // Викликається з кожним тіком. Не спить і не блокує: лише порівнює
    // час і за потреби перемикає вивід.
    void tick(hal::Millis now);

private:
    void apply(bool on);

    hal::OutputPin pin_;
    LedMode        mode_{LedMode::Off};
    bool           state_{false};
    hal::Millis    last_toggle_{0};
    bool           toggle_armed_{false};
};

} // namespace bsp
