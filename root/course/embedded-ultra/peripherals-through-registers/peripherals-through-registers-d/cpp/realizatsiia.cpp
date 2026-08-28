#include <cstdint>
#include <concepts>

namespace Hardware {

    inline constexpr std::uintptr_t PeriphBase   = 0x40000000UL;
    inline constexpr std::uintptr_t Ahb1Base     = PeriphBase + 0x00020000UL;
    inline constexpr std::uintptr_t Apb1Base     = PeriphBase;

    inline constexpr std::uintptr_t RccBase      = Ahb1Base + 0x3800UL;
    inline constexpr std::uintptr_t GpioABase    = Ahb1Base + 0x0000UL;
    inline constexpr std::uintptr_t Tim6Base     = Apb1Base + 0x1000UL;

    struct GpioBlock {
        volatile std::uint32_t MODER;
        volatile std::uint32_t OTYPER;
        volatile std::uint32_t OSPEEDR;
        volatile std::uint32_t PUPDR;
        volatile std::uint32_t IDR;
        volatile std::uint32_t ODR;
        volatile std::uint32_t BSRR;
        volatile std::uint32_t LCKR;
        volatile std::uint32_t AFR[2];
    };

    struct TimerBlock {
        volatile std::uint32_t CR1;
        volatile std::uint32_t CR2;
        std::uint32_t          RESERVED0;
        volatile std::uint32_t DIER;
        volatile std::uint32_t SR;
        volatile std::uint32_t EGR;
        std::uint32_t          RESERVED1[3];
        volatile std::uint32_t CNT;
        volatile std::uint32_t PSC;
        volatile std::uint32_t ARR;
    };

    struct RccBlock {
        volatile std::uint32_t CR;
        volatile std::uint32_t PLLCFGR;
        volatile std::uint32_t CFGR;
        volatile std::uint32_t CIR;
        volatile std::uint32_t AHB1RSTR;
        volatile std::uint32_t AHB2RSTR;
        volatile std::uint32_t AHB3RSTR;
        std::uint32_t          RESERVED0;
        volatile std::uint32_t APB1RSTR;
        volatile std::uint32_t APB2RSTR;
        std::uint32_t          RESERVED1[2];
        volatile std::uint32_t AHB1ENR;
        volatile std::uint32_t AHB2ENR;
        volatile std::uint32_t AHB3ENR;
        std::uint32_t          RESERVED2;
        volatile std::uint32_t APB1ENR;
        volatile std::uint32_t APB2ENR;
    };

    enum class PinMode : std::uint32_t {
        Input     = 0b00,
        Output    = 0b01,
        Alternate = 0b10,
        Analog    = 0b11
    };

    class OutputPin {
    private:
        GpioBlock* const port_;
        const std::uint8_t pinIndex_;

    public:
        constexpr OutputPin(std::uintptr_t portAddress, std::uint8_t pin) noexcept
            : port_(reinterpret_cast<GpioBlock*>(portAddress)), pinIndex_(pin) {}

        void init() const noexcept {
            const std::uint32_t shift = pinIndex_ * 2;
            port_->MODER = (port_->MODER & ~(0b11UL << shift)) | (static_cast<std::uint32_t>(PinMode::Output) << shift);
            port_->OTYPER &= ~(1UL << pinIndex_);       // Push-Pull
            port_->OSPEEDR &= ~(0b11UL << shift);      // Low speed
            port_->PUPDR &= ~(0b11UL << shift);        // No pull
        }

        void setHigh() const noexcept {
            port_->BSRR = (1UL << pinIndex_);
        }

        void setLow() const noexcept {
            port_->BSRR = (1UL << (pinIndex_ + 16));
        }
    };

    class MillisecondTimer {
    private:
        TimerBlock* const timer_;

    public:
        explicit constexpr MillisecondTimer(std::uintptr_t timerAddress) noexcept
            : timer_(reinterpret_cast<TimerBlock*>(timerAddress)) {}

        void start(std::uint32_t busClockHz) const noexcept {
            timer_->PSC = (busClockHz / 1000UL) - 1UL;
            timer_->ARR = 0xFFFFUL;
            timer_->EGR = 1UL;          // Генерація події для оновлення тіньових регістрів
            timer_->SR  = 0UL;          // Скидання прапорця
            timer_->CR1 |= (1UL << 0);   // Counter Enable
        }

        void delay(std::uint16_t ms) const noexcept {
            const auto start = static_cast<std::uint16_t>(timer_->CNT);
            while (static_cast<std::uint16_t>(timer_->CNT - start) < ms) {
                // Опитування лічильника з захистом від переповнення
            }
        }
    };

} // namespace Hardware

int main() {
    // 1. Подача тактування
    auto* rcc = reinterpret_cast<Hardware::RccBlock*>(Hardware::RccBase);
    rcc->AHB1ENR |= (1UL << 0);  // GPIOA
    rcc->APB1ENR |= (1UL << 4);  // TIM6
    (void)rcc->AHB1ENR;

    // 2. Створення об'єктів периферії
    const Hardware::OutputPin led(Hardware::GpioABase, 5);
    const Hardware::MillisecondTimer timer(Hardware::Tim6Base);

    led.init();
    timer.start(16000000UL);

    while (true) {
        led.setHigh();
        timer.delay(500);

        led.setLow();
        timer.delay(500);
    }
}
