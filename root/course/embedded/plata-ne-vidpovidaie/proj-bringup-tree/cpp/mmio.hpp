// Типізований доступ до апаратури STM32F4. Адреса регістра — параметр
// шаблона, тож помилитися базою можна рівно один раз: у місці оголошення,
// а не в кожній п'ятій рядковій операції з бітами.
#pragma once

#include <cstdint>

namespace bringup::mmio {

inline volatile std::uint32_t& at(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<volatile std::uint32_t*>(address);
}

template <std::uintptr_t Address>
struct Reg {
    static std::uint32_t read() noexcept { return at(Address); }
    static void write(std::uint32_t value) noexcept { at(Address) = value; }
    static void set(std::uint32_t mask) noexcept { at(Address) = at(Address) | mask; }
    static void clear(std::uint32_t mask) noexcept { at(Address) = at(Address) & ~mask; }
    static void modify(std::uint32_t clear_mask, std::uint32_t set_mask) noexcept
    {
        at(Address) = (at(Address) & ~clear_mask) | set_mask;
    }
    static bool any(std::uint32_t mask) noexcept { return (at(Address) & mask) != 0U; }
};

// Жодного нескінченного очікування: прошивка перевіряє залізо, тож не має
// права повіснути на регістрі, який ніколи не зміниться.
template <class Predicate>
[[nodiscard]] bool wait_until(Predicate predicate, std::uint32_t tries) noexcept
{
    while (tries > 0U) {
        if (predicate()) {
            return true;
        }
        --tries;
    }
    return false;
}

inline constexpr std::uint32_t core_hz = 16'000'000U;   // HSI, без PLL
inline constexpr std::uint32_t pclk1_hz = 16'000'000U;
inline constexpr std::uint32_t hse_hz = 8'000'000U;

inline void delay_loops(std::uint32_t loops) noexcept
{
    volatile std::uint32_t n = loops;
    while (n > 0U) {
        --n;
    }
}

// Груба затримка: тіло циклу — близько чотирьох тактів. Точності тут не
// потрібно, потрібне «не менше ніж».
inline void delay_us(std::uint32_t us) noexcept
{
    delay_loops(us * (core_hz / 4'000'000U));
}

// ---------------- RCC ----------------
namespace rcc {
inline constexpr std::uintptr_t base = 0x4002'3800U;
using cr      = Reg<base + 0x00U>;
using pllcfgr = Reg<base + 0x04U>;
using cfgr    = Reg<base + 0x08U>;
using ahb1enr = Reg<base + 0x30U>;
using apb1enr = Reg<base + 0x40U>;
using apb2enr = Reg<base + 0x44U>;

inline constexpr std::uint32_t hsion = 1U << 0;
inline constexpr std::uint32_t hsirdy = 1U << 1;
inline constexpr std::uint32_t hseon = 1U << 16;
inline constexpr std::uint32_t hserdy = 1U << 17;
inline constexpr std::uint32_t pllon = 1U << 24;
inline constexpr std::uint32_t pllrdy = 1U << 25;
inline constexpr std::uint32_t sw_mask = 3U << 0;
inline constexpr std::uint32_t sws_mask = 3U << 2;
inline constexpr std::uint32_t pllsrc_hse = 1U << 22;
inline constexpr std::uint32_t i2c1en = 1U << 21;   // APB1
inline constexpr std::uint32_t adc1en = 1U << 8;    // APB2
}  // namespace rcc

// ---------------- GPIO ----------------
enum class Mode : std::uint32_t { input = 0, output = 1, alternate = 2, analog = 3 };
enum class OutputType : std::uint32_t { push_pull = 0, open_drain = 1 };
enum class Pull : std::uint32_t { none = 0, up = 1, down = 2 };

struct Port {
    std::uintptr_t base;
    std::uint32_t clock_bit;   // біт у RCC_AHB1ENR
};

inline constexpr Port porta{0x4002'0000U, 1U << 0};
inline constexpr Port portb{0x4002'0400U, 1U << 1};

struct Pin {
    Port port;
    std::uint32_t number;

    void enable_clock() const noexcept
    {
        rcc::ahb1enr::set(port.clock_bit);
        static_cast<void>(rcc::ahb1enr::read());   // такт затримки шини
    }

    // MODER перемикаємо ОСТАННІМ: спершу тип виходу, підтяжка й швидкість,
    // інакше вивід на мить вилізе на лінію в невідомому стані.
    void configure(Mode mode,
                   OutputType type = OutputType::push_pull,
                   Pull pull = Pull::none) const noexcept
    {
        const std::uint32_t two = number * 2U;
        at(port.base + 0x04U) = (at(port.base + 0x04U) & ~(1U << number))
                              | (static_cast<std::uint32_t>(type) << number);
        at(port.base + 0x0CU) = (at(port.base + 0x0CU) & ~(3U << two))
                              | (static_cast<std::uint32_t>(pull) << two);
        at(port.base + 0x08U) = (at(port.base + 0x08U) & ~(3U << two)) | (2U << two);
        at(port.base + 0x00U) = (at(port.base + 0x00U) & ~(3U << two))
                              | (static_cast<std::uint32_t>(mode) << two);
    }

    void select_alternate(std::uint32_t function) const noexcept
    {
        const std::uintptr_t reg = port.base + (number < 8U ? 0x20U : 0x24U);
        const std::uint32_t shift = (number % 8U) * 4U;
        at(reg) = (at(reg) & ~(0xFU << shift)) | (function << shift);
    }

    void write(bool level) const noexcept { at(port.base + 0x18U) = level ? set_mask() : reset_mask(); }
    [[nodiscard]] bool read() const noexcept { return (at(port.base + 0x10U) & set_mask()) != 0U; }

    [[nodiscard]] constexpr std::uint32_t set_mask() const noexcept { return 1U << number; }
    [[nodiscard]] constexpr std::uint32_t reset_mask() const noexcept { return 1U << (number + 16U); }
};

// ---------------- I2C1 (SCL = PB6, SDA = PB7, AF4) ----------------
namespace i2c1 {
inline constexpr std::uintptr_t base = 0x4000'5400U;
using cr1   = Reg<base + 0x00U>;
using cr2   = Reg<base + 0x04U>;
using dr    = Reg<base + 0x10U>;
using sr1   = Reg<base + 0x14U>;
using sr2   = Reg<base + 0x18U>;
using ccr   = Reg<base + 0x1CU>;
using trise = Reg<base + 0x20U>;

inline constexpr std::uint32_t pe = 1U << 0;
inline constexpr std::uint32_t start = 1U << 8;
inline constexpr std::uint32_t stop = 1U << 9;
inline constexpr std::uint32_t swrst = 1U << 15;
inline constexpr std::uint32_t flag_sb = 1U << 0;     // SR1
inline constexpr std::uint32_t flag_addr = 1U << 1;   // SR1
inline constexpr std::uint32_t flag_af = 1U << 10;    // SR1: NACK
inline constexpr std::uint32_t flag_busy = 1U << 1;   // SR2
inline constexpr std::uint32_t alternate_function = 4U;
}  // namespace i2c1

// ---------------- ADC1 і спільний блок ----------------
namespace adc1 {
inline constexpr std::uintptr_t base = 0x4001'2000U;
using sr    = Reg<base + 0x00U>;
using cr1   = Reg<base + 0x04U>;
using cr2   = Reg<base + 0x08U>;
using smpr1 = Reg<base + 0x0CU>;
using sqr1  = Reg<base + 0x2CU>;
using sqr3  = Reg<base + 0x34U>;
using dr    = Reg<base + 0x4CU>;
using ccr   = Reg<0x4001'2300U + 0x04U>;

inline constexpr std::uint32_t eoc = 1U << 1;
inline constexpr std::uint32_t adon = 1U << 0;
inline constexpr std::uint32_t swstart = 1U << 30;
inline constexpr std::uint32_t adcpre_mask = 3U << 16;
inline constexpr std::uint32_t adcpre_div4 = 1U << 16;
inline constexpr std::uint32_t tsvrefe = 1U << 23;
inline constexpr std::uint32_t channel_vrefint = 17U;

// Заводська константа VREFINT (сирий код каналу при VDDA = 3.30 В).
// Адреса — для STM32F42x/F43x; на F405/F407 комірка часто не запрограмована.
inline constexpr std::uintptr_t vrefint_cal = 0x1FFF'7A2AU;
}  // namespace adc1

}  // namespace bringup::mmio
