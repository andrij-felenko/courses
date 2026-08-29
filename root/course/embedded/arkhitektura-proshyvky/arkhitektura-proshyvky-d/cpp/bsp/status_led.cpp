// bsp/status_led.cpp — реалізація індикатора.
#include "bsp/status_led.hpp"

namespace bsp {
namespace {

constexpr hal::Millis kBlinkSlowPeriod{1000};
constexpr hal::Millis kBlinkFastPeriod{150};

} // namespace

StatusLed::StatusLed(hal::OutputPin pin) : pin_{pin}
{
    pin_.configure(hal::PinMode::OutputPushPull);
    apply(false);
}

void StatusLed::apply(bool on)
{
    state_ = on;
    pin_.write(on);
}

void StatusLed::set_mode(LedMode mode)
{
    if (mode_ == mode) {
        return;
    }
    mode_ = mode;

    switch (mode) {
    case LedMode::Off:
        apply(false);
        break;
    case LedMode::On:
        apply(true);
        break;
    default:
        // Миготіння починаємо з увімкненого стану, щоб зміна режиму була
        // видима оком одразу, а не через півперіоду.
        apply(true);
        toggle_armed_ = false;
        break;
    }
}

void StatusLed::tick(hal::Millis now)
{
    if (mode_ == LedMode::Off || mode_ == LedMode::On) {
        return;
    }

    if (!toggle_armed_) {
        last_toggle_  = now;
        toggle_armed_ = true;
        return;
    }

    const auto half = ((mode_ == LedMode::BlinkFast) ? kBlinkFastPeriod
                                                     : kBlinkSlowPeriod) / 2;
    if ((now - last_toggle_) >= half) {
        last_toggle_ = now;
        apply(!state_);
    }
}

} // namespace bsp
