// platform.hpp — карта периферії STM32F4, потрібної цьому прикладу.
//
// Свідомо без заголовків виробника: тут видно кожну адресу й кожен біт,
// а саме вони і є предметом розмови про безпечний стан.
#pragma once

#include "reg.hpp"

namespace stm32 {

inline constexpr std::uint32_t cpu_hz = 168'000'000U;

// ---- RCC: тактування й причина скидання ---------------------------------
namespace rcc {
inline constexpr std::uintptr_t base = 0x4002'3800U;

using ahb1enr = hw::Register<base + 0x30U>;
using apb1enr = hw::Register<base + 0x40U>;
using apb2enr = hw::Register<base + 0x44U>;
using csr = hw::Register<base + 0x74U>;

inline constexpr std::uint32_t gpioa_en = 1U << 0;
inline constexpr std::uint32_t pwr_en = 1U << 28;
inline constexpr std::uint32_t usart2_en = 1U << 17;
inline constexpr std::uint32_t tim1_en = 1U << 0;

// Прапорці причини скидання. Тримаються, доки їх не зняти через rmvf.
inline constexpr std::uint32_t low_power_rst = 1U << 31;
inline constexpr std::uint32_t wwdg_rst = 1U << 30;
inline constexpr std::uint32_t iwdg_rst = 1U << 29;
inline constexpr std::uint32_t soft_rst = 1U << 28;
inline constexpr std::uint32_t por_rst = 1U << 27;
inline constexpr std::uint32_t pin_rst = 1U << 26;
inline constexpr std::uint32_t bor_rst = 1U << 25;
inline constexpr std::uint32_t rmvf = 1U << 24;
} // namespace rcc

// ---- PWR: програмований монітор живлення (PVD) --------------------------
namespace pwr {
inline constexpr std::uintptr_t base = 0x4000'7000U;

using cr = hw::Register<base + 0x00U>;
using csr = hw::Register<base + 0x04U>;

using pls = hw::Field<5, 3>;                     // поріг спрацювання PVD
inline constexpr std::uint32_t pvde = 1U << 4;   // дозвіл монітора
inline constexpr std::uint32_t pvdo = 1U << 2;   // 1 = Vdd нижче порога
inline constexpr std::uint32_t level_2v9 = 6U;   // PLS = 110 -> ≈2.9 В
} // namespace pwr

// ---- GPIOA ---------------------------------------------------------------
namespace gpioa {
inline constexpr std::uintptr_t base = 0x4002'0000U;

using moder = hw::Register<base + 0x00U>;
using otyper = hw::Register<base + 0x04U>;
using ospeedr = hw::Register<base + 0x08U>;
using pupdr = hw::Register<base + 0x0CU>;
using idr = hw::Register<base + 0x10U>;
using bsrr = hw::Register<base + 0x18U>;
using afrl = hw::Register<base + 0x20U>;

enum class Mode : std::uint32_t { input = 0U, output = 1U, alternate = 2U, analog = 3U };
enum class Pull : std::uint32_t { none = 0U, up = 1U, down = 2U };

inline void set_mode(unsigned pin, Mode mode) noexcept
{
    moder::modify(0b11U << (pin * 2U), static_cast<std::uint32_t>(mode) << (pin * 2U));
}

inline void set_pull(unsigned pin, Pull pull) noexcept
{
    pupdr::modify(0b11U << (pin * 2U), static_cast<std::uint32_t>(pull) << (pin * 2U));
}

inline void set_alternate(unsigned pin, unsigned function) noexcept
{
    afrl::modify(0xFU << (pin * 4U), function << (pin * 4U));
}

inline void write_pin(unsigned pin, bool high) noexcept
{
    bsrr::write(high ? (1U << pin) : (1U << (pin + 16U)));
}

[[nodiscard]] inline bool read_pin(unsigned pin) noexcept
{
    return idr::any(1U << pin);
}
} // namespace gpioa

// ---- TIM1: силовий ШІМ мостового драйвера --------------------------------
namespace tim1 {
inline constexpr std::uintptr_t base = 0x4001'0000U;

using cr1 = hw::Register<base + 0x00U>;
using ccmr1 = hw::Register<base + 0x18U>;
using ccer = hw::Register<base + 0x20U>;
using psc = hw::Register<base + 0x28U>;
using arr = hw::Register<base + 0x2CU>;
using ccr1 = hw::Register<base + 0x34U>;
using bdtr = hw::Register<base + 0x44U>;

inline constexpr std::uint32_t cen = 1U << 0;
inline constexpr std::uint32_t moe = 1U << 15; // головний дозвіл виходів
inline constexpr std::uint32_t cc1e = 1U << 0;
inline constexpr std::uint32_t cc1ne = 1U << 2;
} // namespace tim1

// ---- IWDG: сторож на власному RC ≈32 кГц ---------------------------------
namespace iwdg {
inline constexpr std::uintptr_t base = 0x4000'3000U;

using kr = hw::Register<base + 0x00U>;
using pr = hw::Register<base + 0x04U>;
using rlr = hw::Register<base + 0x08U>;
using sr = hw::Register<base + 0x0CU>;

inline constexpr std::uint32_t key_feed = 0x0000'AAAAU;
inline constexpr std::uint32_t key_unlock = 0x0000'5555U;
inline constexpr std::uint32_t key_start = 0x0000'CCCCU;
} // namespace iwdg

// ---- USART2: діагностичний канал -----------------------------------------
namespace usart2 {
inline constexpr std::uintptr_t base = 0x4000'4400U;

using sr = hw::Register<base + 0x00U>;
using dr = hw::Register<base + 0x04U>;
using brr = hw::Register<base + 0x08U>;
using cr1 = hw::Register<base + 0x0CU>;

inline constexpr std::uint32_t txe = 1U << 7;
inline constexpr std::uint32_t tc = 1U << 6;
inline constexpr std::uint32_t ue = 1U << 13;
inline constexpr std::uint32_t te = 1U << 3;
} // namespace usart2

// ---- Ядро Cortex-M4 -------------------------------------------------------
namespace systick {
inline constexpr std::uintptr_t base = 0xE000'E010U;

using csr = hw::Register<base + 0x00U>;
using rvr = hw::Register<base + 0x04U>;
using cvr = hw::Register<base + 0x08U>;

inline constexpr std::uint32_t enable = 0x7U; // ENABLE | TICKINT | CLKSOURCE
} // namespace systick

namespace scb {
inline constexpr std::uintptr_t base = 0xE000'ED00U;

using aircr = hw::Register<base + 0x0CU>;
using cfsr = hw::Register<base + 0x28U>;
using hfsr = hw::Register<base + 0x2CU>;

inline constexpr std::uint32_t aircr_key = 0x05FA'0000U;
inline constexpr std::uint32_t sysresetreq = 1U << 2;
} // namespace scb

[[noreturn]] inline void system_reset() noexcept
{
    hw::dsb();
    scb::aircr::write(scb::aircr_key | scb::sysresetreq);
    hw::dsb();
    for (;;) {
        // ядро вже перезапускається
    }
}

} // namespace stm32
