// ports/host_mock/mock_gpio.cpp — виводи, яких немає.
#include "ports/host_mock/host_mocks.hpp"

namespace port {

void MockGpioPort::configure(std::uint8_t pin, hal::PinMode mode)
{
    if (pin < kPins) {
        mode_[pin] = mode;
    }
}

void MockGpioPort::set(std::uint8_t pin, bool level)
{
    if (pin >= kPins) {
        return;
    }
    if (level_[pin] != level) {
        ++toggles_[pin];
    }
    level_[pin] = level;
}

bool MockGpioPort::get(std::uint8_t pin) const
{
    return (pin < kPins) && level_[pin];
}

unsigned MockGpioPort::toggles(std::uint8_t pin) const
{
    return (pin < kPins) ? toggles_[pin] : 0;
}

} // namespace port
