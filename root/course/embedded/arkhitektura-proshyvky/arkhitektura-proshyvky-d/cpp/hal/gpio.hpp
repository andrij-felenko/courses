// hal/gpio.hpp — вивід як об'єкт.
// OutputPin знає про активний рівень і сам його перевертає, тож драйвер
// світлодіода ніколи не питає, катодом чи анодом той підключений.
#pragma once

#include <cstdint>

namespace hal {

enum class PinMode : std::uint8_t {
    Input,
    InputPullUp,
    OutputPushPull,
    OutputOpenDrain
};

class IGpioPort {
public:
    virtual ~IGpioPort() = default;

    IGpioPort(const IGpioPort&) = delete;
    IGpioPort& operator=(const IGpioPort&) = delete;

    virtual void configure(std::uint8_t pin, PinMode mode) = 0;
    virtual void set(std::uint8_t pin, bool level) = 0;
    [[nodiscard]] virtual bool get(std::uint8_t pin) const = 0;

protected:
    IGpioPort() = default;
};

class OutputPin {
public:
    constexpr OutputPin(IGpioPort& port, std::uint8_t pin, bool active_low = false) noexcept
        : port_{&port}, pin_{pin}, active_low_{active_low} {}

    void configure(PinMode mode = PinMode::OutputPushPull) const { port_->configure(pin_, mode); }

    // true означає «активний стан», а не «висока напруга».
    void write(bool on) const { port_->set(pin_, active_low_ ? !on : on); }

    [[nodiscard]] bool read() const
    {
        const bool raw = port_->get(pin_);
        return active_low_ ? !raw : raw;
    }

    void toggle() const { write(!read()); }

private:
    IGpioPort*   port_;
    std::uint8_t pin_;
    bool         active_low_;
};

} // namespace hal
