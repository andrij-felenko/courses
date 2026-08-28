// Наївна ініціалізація тактування з девборди (C++)
#include <cstdint>

namespace bsp::naive {

inline volatile uint32_t& reg_rcc_cr      = *reinterpret_cast<volatile uint32_t*>(0x40023800);
inline volatile uint32_t& reg_rcc_pllcfgr = *reinterpret_cast<volatile uint32_t*>(0x40023804);
inline volatile uint32_t& reg_rcc_cfgr    = *reinterpret_cast<volatile uint32_t*>(0x40023808);

constexpr uint32_t hse_on_bit   = 1UL << 16;
constexpr uint32_t hse_rdy_bit  = 1UL << 17;
constexpr uint32_t pll_on_bit   = 1UL << 24;
constexpr uint32_t pll_rdy_bit  = 1UL << 25;
constexpr uint32_t sw_pll_bits  = 0x02UL;
constexpr uint32_t sws_pll_bits = 0x08UL;

void init_clock_naive() noexcept {
    // Активація контуру HSE
    reg_rcc_cr |= hse_on_bit;

    // НЕБЕЗПЕКА: Зависання в разі апаратної проблеми з кварцом
    while (!(reg_rcc_cr & hse_rdy_bit)) {
        // Нескінченне блокування
    }

    // Налаштування PLL
    reg_rcc_pllcfgr = (8 << 0) | (336 << 6) | (0 << 16);
    reg_rcc_cr |= pll_on_bit;
    while (!(reg_rcc_cr & pll_rdy_bit));

    // Перемикання джерела тактування
    reg_rcc_cfgr = (reg_rcc_cfgr & ~0x03UL) | sw_pll_bits;
    while ((reg_rcc_cfgr & 0x0CUL) != sws_pll_bits);
}

} // namespace bsp::naive
