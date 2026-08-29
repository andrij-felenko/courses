#pragma once

#include <bit>
#include <cstdint>

/*
 * Доступ до регістрів STM32F42x/43x. На відміну від C-варіанта, зсуви
 * бітових полів тут не пишуться руками: маска сама їх знає, а компілятор
 * рахує все на етапі компіляції.
 */

namespace bsp::mmio {

/* Бітове поле регістра: зсув виводиться з маски через std::countr_zero */
struct Field {
    std::uint32_t mask;

    constexpr std::uint32_t operator()(std::uint32_t value) const noexcept {
        return (value << std::countr_zero(mask)) & mask;
    }

    constexpr std::uint32_t extract(std::uint32_t reg) const noexcept {
        return (reg & mask) >> std::countr_zero(mask);
    }
};

/* Читання-модифікація-запис одним виразом замість трьох рядків із ~mask */
inline void modify(volatile std::uint32_t& reg, std::uint32_t clear_mask,
                   std::uint32_t set_bits) noexcept {
    reg = (reg & ~clear_mask) | set_bits;
}

/* Очікування стану біта з обмеженим числом спроб: вічного while у драйвері немає */
inline bool wait_until(const volatile std::uint32_t& reg, std::uint32_t mask,
                       std::uint32_t expected, std::uint32_t cycles) noexcept {
    while ((reg & mask) != expected) {
        if (cycles-- == 0U) {
            return false;
        }
    }
    return true;
}

} // namespace bsp::mmio

namespace bsp::soc {

struct Rcc {
    volatile std::uint32_t cr;          // 0x00
    volatile std::uint32_t pllcfgr;     // 0x04
    volatile std::uint32_t cfgr;        // 0x08
    volatile std::uint32_t cir;         // 0x0C
    volatile std::uint32_t reserved0[8];// 0x10..0x2C регістри скидання шин
    volatile std::uint32_t ahb1enr;     // 0x30
    volatile std::uint32_t ahb2enr;     // 0x34
    volatile std::uint32_t ahb3enr;     // 0x38
    volatile std::uint32_t reserved1;   // 0x3C
    volatile std::uint32_t apb1enr;     // 0x40
    volatile std::uint32_t apb2enr;     // 0x44
};

struct Flash {
    volatile std::uint32_t acr;
};

struct Pwr {
    volatile std::uint32_t cr;
    volatile std::uint32_t csr;
};

struct Gpio {
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

/* Функції, а не глобальні посилання: reinterpret_cast не є константним
   виразом, і функція знімає питання порядку статичної ініціалізації */
inline Rcc&   rcc()   noexcept { return *reinterpret_cast<Rcc*>(0x40023800UL); }
inline Flash& flash() noexcept { return *reinterpret_cast<Flash*>(0x40023C00UL); }
inline Pwr&   pwr()   noexcept { return *reinterpret_cast<Pwr*>(0x40007000UL); }
inline Gpio&  gpioa() noexcept { return *reinterpret_cast<Gpio*>(0x40020000UL); }

/* TIM1_BDTR: біт MOE гасить усі виходи силового мосту одним записом */
inline volatile std::uint32_t& tim1_bdtr() noexcept {
    return *reinterpret_cast<volatile std::uint32_t*>(0x40010000UL + 0x44UL);
}

inline volatile std::uint32_t& scb_aircr() noexcept {
    return *reinterpret_cast<volatile std::uint32_t*>(0xE000ED0CUL);
}

inline constexpr std::uint32_t tim_bdtr_moe = 1U << 15;
inline constexpr std::uint32_t sysresetreq  = 0x05FA0004UL;

namespace cr {
inline constexpr std::uint32_t hsion  = 1U << 0;
inline constexpr std::uint32_t hsirdy = 1U << 1;
inline constexpr std::uint32_t hseon  = 1U << 16;
inline constexpr std::uint32_t hserdy = 1U << 17;
inline constexpr std::uint32_t csson  = 1U << 19;
inline constexpr std::uint32_t pllon  = 1U << 24;
inline constexpr std::uint32_t pllrdy = 1U << 25;
} // namespace cr

namespace cfgr {
inline constexpr mmio::Field sw{0x3U << 0};
inline constexpr mmio::Field sws{0x3U << 2};
inline constexpr mmio::Field hpre{0xFU << 4};
inline constexpr mmio::Field ppre1{0x7U << 10};
inline constexpr mmio::Field ppre2{0x7U << 13};
inline constexpr mmio::Field mco1{0x3U << 21};
inline constexpr mmio::Field mco1pre{0x7U << 24};

inline constexpr std::uint32_t src_hsi  = 0b00;   // коди для sw і sws однакові
inline constexpr std::uint32_t src_pll  = 0b10;
inline constexpr std::uint32_t ahb_div1 = 0b0000;
inline constexpr std::uint32_t apb_div1 = 0b000;
inline constexpr std::uint32_t apb_div2 = 0b100;
inline constexpr std::uint32_t apb_div4 = 0b101;
} // namespace cfgr

namespace cir {
inline constexpr std::uint32_t cssf = 1U << 7;
inline constexpr std::uint32_t cssc = 1U << 23;
} // namespace cir

namespace acr {
inline constexpr mmio::Field  latency{0x7U << 0};
inline constexpr std::uint32_t prften = 1U << 8;
inline constexpr std::uint32_t icen   = 1U << 9;
inline constexpr std::uint32_t dcen   = 1U << 10;
inline constexpr std::uint32_t icrst  = 1U << 11;
inline constexpr std::uint32_t dcrst  = 1U << 12;
} // namespace acr

namespace pwr_cr {
inline constexpr mmio::Field vos{0x3U << 14};
} // namespace pwr_cr

namespace pwr_csr {
inline constexpr std::uint32_t vosrdy = 1U << 14;
} // namespace pwr_csr

inline constexpr std::uint32_t apb1enr_pwren   = 1U << 28;
inline constexpr std::uint32_t ahb1enr_gpioaen = 1U << 0;

} // namespace bsp::soc
