#include <cstdint>

namespace mcu {

// Безпечна типізована обгортка над апаратним регістром
template <std::uintptr_t Address>
struct Register {
    static void write(std::uint32_t value) noexcept {
        *reinterpret_cast<volatile std::uint32_t*>(Address) = value;
    }

    static std::uint32_t read() noexcept {
        return *reinterpret_cast<volatile std::uint32_t*>(Address);
    }

    static void set_bits(std::uint32_t mask) noexcept {
        write(read() | mask);
    }

    static void clear_bits(std::uint32_t mask) noexcept {
        write(read() & ~mask);
    }

    static void modify(std::uint32_t clear_mask, std::uint32_t set_mask) noexcept {
        write((read() & ~clear_mask) | set_mask);
    }
};

// Карта периферії STM32F4
inline constexpr std::uintptr_t periph_base     = 0x40000000UL;
inline constexpr std::uintptr_t ahb1periph_base = periph_base + 0x00020000UL;
inline constexpr std::uintptr_t rcc_base        = ahb1periph_base + 0x3800UL;
inline constexpr std::uintptr_t gpioc_base      = ahb1periph_base + 0x0800UL;

// Регістри тактування та портів
using RccAhb1Enr  = Register<rcc_base + 0x30UL>;
using GpiocModer  = Register<gpioc_base + 0x00UL>;
using GpiocOtyper = Register<gpioc_base + 0x04UL>;
using GpiocOspeed = Register<gpioc_base + 0x08UL>;
using GpiocPupdr  = Register<gpioc_base + 0x0CUL>;
using GpiocBsrr   = Register<gpioc_base + 0x18UL>;

enum class PinMode : std::uint32_t {
    Input     = 0b00,
    Output    = 0b01,
    Alternate = 0b10,
    Analog    = 0b11
};

enum class ActivePolarity {
    High,
    Low
};

template <std::uint8_t PinNumber, ActivePolarity Polarity = ActivePolarity::High>
class OutputPin {
    static_assert(PinNumber < 16, "Pin number must be between 0 and 15");

public:
    static void init() noexcept {
        // Конфігурація режиму General Purpose Output
        constexpr std::uint32_t mask = 0b11UL << (PinNumber * 2);
        constexpr std::uint32_t val  = static_cast<std::uint32_t>(PinMode::Output) << (PinNumber * 2);
        GpiocModer::modify(mask, val);

        // Push-pull вихід
        GpiocOtyper::clear_bits(1UL << PinNumber);

        // Low speed для зменшення шуму живлення
        GpiocOspeed::clear_bits(0b11UL << (PinNumber * 2));

        // Без підтяжки
        GpiocPupdr::clear_bits(0b11UL << (PinNumber * 2));

        turn_off();
    }

    static void set_raw_high() noexcept {
        GpiocBsrr::write(1UL << PinNumber);
    }

    static void set_raw_low() noexcept {
        GpiocBsrr::write(1UL << (PinNumber + 16));
    }

    static void turn_on() noexcept {
        if constexpr (Polarity == ActivePolarity::High) {
            set_raw_high();
        } else {
            set_raw_low();
        }
    }

    static void turn_off() noexcept {
        if constexpr (Polarity == ActivePolarity::High) {
            set_raw_low();
        } else {
            set_raw_high();
        }
    }

    static void toggle(bool state) noexcept {
        if (state) {
            turn_on();
        } else {
            turn_off();
        }
    }
};

} // namespace mcu

namespace {

void delay_ticks(volatile std::uint32_t ticks) noexcept {
    while (ticks--) {
        __asm__ volatile ("nop");
    }
}

} // namespace

int main() {
    // 1. Дозвіл тактування порту GPIOC (біт 2)
    mcu::RccAhb1Enr::set_bits(1UL << 2);

    // Бар'єр пам'яті для завершення транзакції на шині
    __asm__ volatile ("dmb" ::: "memory");

    // 2. Ініціалізація виводу світлодіода (PC13, Active High)
    using Led = mcu::OutputPin<13, mcu::ActivePolarity::High>;
    Led::init();

    // 3. Нескінченний цикл
    while (true) {
        Led::turn_on();
        delay_ticks(500000);

        Led::turn_off();
        delay_ticks(500000);
    }

    return 0;
}
