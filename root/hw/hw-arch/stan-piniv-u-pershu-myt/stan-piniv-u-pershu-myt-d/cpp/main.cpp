#include <cstdint>
#include <span>
#include <concepts>

// Високонадійний C++20 модуль нульової вартості (Zero-Cost Abstraction)
namespace SystemHw {

enum class PinMode : uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

enum class PullMode : uint32_t {
    Floating = 0b00,
    PullUp   = 0b01,
    PullDown = 0b10
};

enum class PinSpeed : uint32_t {
    LowSpeed      = 0b00,
    MediumSpeed   = 0b01,
    HighSpeed     = 0b10,
    VeryHighSpeed = 0b11
};

enum class InitialState : uint32_t {
    InactiveLow,
    ActiveHigh
};

struct GpioRegisters {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
};

struct SafePinDescriptor {
    uintptr_t port_base;
    uint32_t pin_index;
    PinMode mode;
    PullMode pull;
    PinSpeed speed;
    InitialState initial_level;
    bool lock_after_init;
};

class EarlyPinSafetyGuard {
public:
    template <std::size_t N>
    static void configure_safety_pins(const SafePinDescriptor (&pins)[N]) noexcept {
        for (const auto& pin : pins) {
            auto* port = reinterpret_cast<GpioRegisters*>(pin.port_base);
            const uint32_t shift2 = pin.pin_index * 2;

            // 1. Атомарне попереднє встановлення вихідного рівня через BSRR
            if (pin.mode == PinMode::Output) {
                if (pin.initial_level == InitialState::InactiveLow) {
                    port->BSRR = (1UL << (pin.pin_index + 16)); // Скидання в 0
                } else {
                    port->BSRR = (1UL << pin.pin_index);        // Встановлення в 1
                }
            }

            // 2. Налаштування внутрішньої підтяжки
            uint32_t pupdr_val = port->PUPDR & ~(0b11UL << shift2);
            pupdr_val |= (static_cast<uint32_t>(pin.pull) << shift2);
            port->PUPDR = pupdr_val;

            // 3. Налаштування швидкості наростання
            uint32_t speed_val = port->OSPEEDR & ~(0b11UL << shift2);
            speed_val |= (static_cast<uint32_t>(pin.speed) << shift2);
            port->OSPEEDR = speed_val;

            // 4. Перемикання режиму виводу
            uint32_t moder_val = port->MODER & ~(0b11UL << shift2);
            moder_val |= (static_cast<uint32_t>(pin.mode) << shift2);
            port->MODER = moder_val;

            // 5. Апаратне блокування конфігурації за потреби
            if (pin.lock_after_init) {
                const uint32_t mask = (1UL << pin.pin_index);
                port->LCKR = mask | (1UL << 16);
                port->LCKR = mask;
                port->LCKR = mask | (1UL << 16);
                [[maybe_unused]] volatile uint32_t r1 = port->LCKR;
                [[maybe_unused]] volatile uint32_t r2 = port->LCKR;
            }
        }

        // Бар'єр пам'яті для гарантування завершення всіх транзакцій на шині AHB
        asm volatile ("dsb 0xF" ::: "memory");
    }
};

} // namespace SystemHw

// Таблиця критичних пінів системи, обчислена на етапі компіляції
inline constexpr SystemHw::SafePinDescriptor kSafetyCriticalPins[] = {
    { 0x48000000UL, 5, SystemHw::PinMode::Output, SystemHw::PullMode::PullDown, SystemHw::PinSpeed::LowSpeed, SystemHw::InitialState::InactiveLow, true }, // PA5 (Gate Low, Locked)
    { 0x48000400UL, 2, SystemHw::PinMode::Input,  SystemHw::PullMode::PullUp,   SystemHw::PinSpeed::LowSpeed, SystemHw::InitialState::InactiveLow, false } // PB2 (Fault In)
};

extern "C" void SystemInit_EarlyGuard(void) {
    // Вмикання тактування GPIOA та GPIOB
    *reinterpret_cast<volatile uint32_t*>(0x40021000UL + 0x4C) |= (1UL << 0) | (1UL << 1);
    SystemHw::EarlyPinSafetyGuard::configure_safety_pins(kSafetyCriticalPins);
}
