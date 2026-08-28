#include <cstdint>

enum class PinMode : std::uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

enum class OutputType : std::uint32_t {
    PushPull  = 0,
    OpenDrain = 1
};

class GpioPin {
private:
    GpioRegisters* const port_;
    const std::uint8_t pin_;

public:
    constexpr GpioPin(std::uintptr_t portBase, std::uint8_t pin) noexcept
        : port_(reinterpret_cast<GpioRegisters*>(portBase)), pin_(pin) {}

    void configure(PinMode mode, OutputType otype) const noexcept {
        const std::uint32_t shift2 = pin_ * 2;

        /* Налаштування режиму (MODER) */
        port_->MODER = (port_->MODER & ~(0b11UL << shift2)) | (static_cast<std::uint32_t>(mode) << shift2);

        /* Налаштування типу виходу (OTYPER) */
        if (otype == OutputType::OpenDrain) {
            port_->OTYPER |= (1UL << pin_);
        } else {
            port_->OTYPER &= ~(1UL << pin_);
        }
    }

    /* Атомарне встановлення високого рівня (Set) */
    void setHigh() const noexcept {
        port_->BSRR = (1UL << pin_);
    }

    /* Атомарне встановлення низького рівня (Reset) */
    void setLow() const noexcept {
        port_->BSRR = (1UL << (pin_ + 16));
    }
};

class HardwareTimer {
private:
    TimerRegisters* const timer_;

public:
    explicit constexpr HardwareTimer(std::uintptr_t baseAddress) noexcept
        : timer_(reinterpret_cast<TimerRegisters*>(baseAddress)) {}

    void initPrescaler(std::uint32_t busClockHz, std::uint32_t targetFrequencyHz) const noexcept {
        timer_->PSC = (busClockHz / targetFrequencyHz) - 1UL;
        timer_->ARR = 0xFFFFUL;
        timer_->EGR = 1UL;              /* Примусове оновлення тіньового регістра */
        timer_->SR  = 0UL;              /* Скидання прапорця оновлення */
        timer_->CR1 |= (1UL << 0);       /* Вмикання лічильника (CEN) */
    }

    void delayMilliseconds(std::uint16_t ms) const noexcept {
        const auto start = static_cast<std::uint16_t>(timer_->CNT);
        while (static_cast<std::uint16_t>(timer_->CNT - start) < ms) {
            /* Опитування апаратного регістра з обробкою переходу через нуль */
        }
    }
};
