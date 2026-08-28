// main.cpp — Типобезпечний Blinky на C++ з прямим доступом до регістрів
#include <cstdint>

namespace mcu {
    inline constexpr std::uintptr_t rcc_base   = 0x40023800U;
    inline constexpr std::uintptr_t gpioa_base = 0x40020000U;

    struct Rcc {
        volatile std::uint32_t cr;
        volatile std::uint32_t pllcfgr;
        volatile std::uint32_t cfgr;
        volatile std::uint32_t cir;
        volatile std::uint32_t ahb1rstr;
        volatile std::uint32_t ahb2rstr;
        std::uint32_t reserved[2];
        volatile std::uint32_t ahb1enr;
    };

    struct Gpio {
        volatile std::uint32_t moder;
        volatile std::uint32_t otyper;
        volatile std::uint32_t ospeedr;
        volatile std::uint32_t pupdr;
        volatile std::uint32_t idr;
        volatile std::uint32_t odr;
        volatile std::uint32_t bsrr;
    };

    inline auto& rcc   = *reinterpret_cast<Rcc*>(rcc_base);
    inline auto& gpioa = *reinterpret_cast<Gpio*>(gpioa_base);

    [[gnu::noinline]] void delay_cycles(volatile std::uint32_t count) {
        while (count--) {
            asm volatile("nop");
        }
    }
}

int main() {
    // 1. Дозвіл тактування порту GPIOA
    mcu::rcc.ahb1enr |= (1U << 0);

    // 2. Конфігурація PA5 як Digital Output
    mcu::gpioa.moder &= ~(0b11U << (5 * 2));
    mcu::gpioa.moder |=  (0b01U << (5 * 2));

    while (true) {
        mcu::gpioa.odr ^= (1U << 5);
        mcu::delay_cycles(500000U);
    }
}
