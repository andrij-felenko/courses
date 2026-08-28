/* Ідіоматичний C++20 Bring-Up тест із прямим доступом до регістрів через типізовані вказівники */
#include <cstdint>
#include <concepts>

namespace mcu::bringup {

inline constexpr std::uintptr_t rcc_base   = 0x40023800U;
inline constexpr std::uintptr_t gpioa_base = 0x40020000U;
inline constexpr std::uintptr_t gpioc_base = 0x40020800U;

struct rcc_registers {
    volatile std::uint32_t cr;
    volatile std::uint32_t pllcfgr;
    volatile std::uint32_t cfgr;
    volatile std::uint32_t cir;
    volatile std::uint32_t ahb1rstr;
    volatile std::uint32_t ahb2rstr;
    volatile std::uint32_t ahb3rstr;
    std::uint32_t reserved0;
    volatile std::uint32_t ahb1enr;
};

struct gpio_registers {
    volatile std::uint32_t moder;
    volatile std::uint32_t otyper;
    volatile std::uint32_t ospeedr;
    volatile std::uint32_t pupdr;
    volatile std::uint32_t idr;
    volatile std::uint32_t odr;
    volatile std::uint32_t bsrr;
    volatile std::uint32_t lckr;
    volatile std::uint32_t afr[2];
};

auto& rcc   = *reinterpret_cast<rcc_registers*>(rcc_base);
auto& gpioa = *reinterpret_cast<gpio_registers*>(gpioa_base);
auto& gpioc = *reinterpret_cast<gpio_registers*>(gpioc_base);

void delay_cycles(std::uint32_t count) noexcept {
    while (count-- > 0) {
        asm volatile ("nop");
    }
}

void init_hardware() noexcept {
    /* 1. Тактування портів GPIOA та GPIOC */
    rcc.ahb1enr |= (1U << 0) | (1U << 2);

    /* 2. Конфігурація тестового LED (PC13) як цифровий вихід */
    gpioc.moder &= ~(0b11U << (13 * 2));
    gpioc.moder |=  (0b01U << (13 * 2));

    /* 3. Конфігурація PA8 як вивід MCO1 (Alternate Function AF0) */
    gpioa.moder &= ~(0b11U << (8 * 2));
    gpioa.moder |=  (0b10U << (8 * 2));
    gpioa.afr[1] &= ~(0b1111U << ((8 - 8) * 4));

    /* 4. MCO1 джерело HSI, переддільник /4 */
    rcc.cfgr &= ~((0b11U << 21) | (0b111U << 24));
    rcc.cfgr |=  (0b00U << 21) | (0b110U << 24);
}

[[noreturn]] void run_heartbeat() noexcept {
    while (true) {
        gpioc.odr ^= (1U << 13);
        delay_cycles(200'000);
    }
}

} // namespace mcu::bringup

int main() {
    mcu::bringup::init_hardware();
    mcu::bringup::run_heartbeat();
}
