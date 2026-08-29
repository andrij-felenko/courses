// hal/hal_gpio.hpp — контракт однієї цифрової ніжки.
#pragma once

#include <cstdint>
#include <expected>

namespace hal {

enum class Level : std::uint8_t { Low = 0, High = 1 };

enum class GpioError : std::uint8_t { Hardware, NotConfigured };

class IGpioPin {
public:
    virtual ~IGpioPin() = default;

    IGpioPin() = default;
    IGpioPin(const IGpioPin&) = delete;
    IGpioPin& operator=(const IGpioPin&) = delete;

    virtual std::expected<void, GpioError> write(Level level) = 0;
    virtual std::expected<Level, GpioError> read() const = 0;

    std::expected<void, GpioError> set_high() { return write(Level::High); }
    std::expected<void, GpioError> set_low() { return write(Level::Low); }
};

constexpr Level invert(Level level) noexcept
{
    return level == Level::High ? Level::Low : Level::High;
}

}  // namespace hal
