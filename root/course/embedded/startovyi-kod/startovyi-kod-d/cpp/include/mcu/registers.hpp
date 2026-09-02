#pragma once

#include <cstdint>

namespace mcu {

/* Регістр, відображений у пам'ять. Адреса — параметр шаблона, тож у
   машинний код іде безпосередня константа, а тип не дає переплутати
   регістр зі звичайною змінною й загубити volatile. */
template <std::uintptr_t Address>
struct reg32 {
    [[nodiscard]] static std::uint32_t read() noexcept { return raw(); }

    static void write(std::uint32_t value) noexcept { raw() = value; }

    static void set(std::uint32_t mask) noexcept { raw() = raw() | mask; }

    static void clear(std::uint32_t mask) noexcept { raw() = raw() & ~mask; }

    static void modify(std::uint32_t clear_mask, std::uint32_t set_mask) noexcept
    {
        raw() = (raw() & ~clear_mask) | set_mask;
    }

    [[nodiscard]] static bool all_set(std::uint32_t mask) noexcept
    {
        return (read() & mask) == mask;
    }

private:
    [[nodiscard]] static volatile std::uint32_t& raw() noexcept
    {
        return *reinterpret_cast<volatile std::uint32_t*>(Address);
    }
};

/* Машинні інструкції, без яких стартовий код не обходиться */
inline void dsb() noexcept { asm volatile("dsb 0xF" ::: "memory"); }
inline void isb() noexcept { asm volatile("isb 0xF" ::: "memory"); }
inline void wait_for_interrupt() noexcept { asm volatile("wfi"); }
inline void breakpoint() noexcept { asm volatile("bkpt #0"); }

/* System Control Block ядра Cortex-M */
namespace scb {

using vtor  = reg32<0xE000ED08UL>; /* зсув таблиці векторів */
using aircr = reg32<0xE000ED0CUL>; /* скидання й пріоритети */
using shcsr = reg32<0xE000ED24UL>; /* дозвіл системних винятків */
using cpacr = reg32<0xE000ED88UL>; /* доступ до співпроцесорів */
using dhcsr = reg32<0xE000EDF0UL>; /* стан налагоджувача */

inline constexpr std::uint32_t cp10_full = 0b11U << 20; /* одинарна точність */
inline constexpr std::uint32_t cp11_full = 0b11U << 22; /* подвійна точність */
inline constexpr std::uint32_t fpu_full_access = cp10_full | cp11_full;

inline constexpr std::uint32_t memfault_enable = 1U << 16;
inline constexpr std::uint32_t busfault_enable = 1U << 17;
inline constexpr std::uint32_t usgfault_enable = 1U << 18;

inline constexpr std::uint32_t debugger_attached = 1U << 0; /* DHCSR.C_DEBUGEN */

} // namespace scb

/* Дерево тактування STM32F4 */
namespace rcc {

using cr      = reg32<0x40023800UL>;
using pllcfgr = reg32<0x40023804UL>;
using cfgr    = reg32<0x40023808UL>;
using cir     = reg32<0x4002380CUL>;
using ahb1enr = reg32<0x40023830UL>;
using apb2enr = reg32<0x40023844UL>;

inline constexpr std::uint32_t hsi_on   = 1U << 0;
inline constexpr std::uint32_t hse_on   = 1U << 16;
inline constexpr std::uint32_t hse_ready = 1U << 17;
inline constexpr std::uint32_t hse_bypass = 1U << 18;
inline constexpr std::uint32_t css_on   = 1U << 19; /* сторож зриву кварцу */
inline constexpr std::uint32_t pll_on   = 1U << 24;
inline constexpr std::uint32_t pll_ready = 1U << 25;

inline constexpr std::uint32_t pllcfgr_reset = 0x2400'3010U; /* заводське */
inline constexpr std::uint32_t pllsrc_hse    = 1U << 22;

inline constexpr std::uint32_t sw_mask    = 0b11U << 0;
inline constexpr std::uint32_t sw_pll     = 0b10U << 0;
inline constexpr std::uint32_t sws_mask   = 0b11U << 2;
inline constexpr std::uint32_t sws_pll    = 0b10U << 2;
inline constexpr std::uint32_t hpre_div1  = 0b0000U << 4;  /* AHB  = SYSCLK     */
inline constexpr std::uint32_t ppre1_div4 = 0b101U << 10;  /* APB1 = SYSCLK / 4 */
inline constexpr std::uint32_t ppre2_div2 = 0b100U << 13;  /* APB2 = SYSCLK / 2 */

} // namespace rcc

/* Контролер Flash: затримки читання й кеші */
namespace flash {

using acr = reg32<0x40023C00UL>;

inline constexpr std::uint32_t latency_5ws = 5U << 0;
inline constexpr std::uint32_t prefetch    = 1U << 8;
inline constexpr std::uint32_t icache      = 1U << 9;
inline constexpr std::uint32_t dcache      = 1U << 10;

} // namespace flash

} // namespace mcu
