// scb.hpp — регістри ядра Cortex-M як типи, а не як макроси з адресами.
//
// Адреса регістра відома на етапі компіляції, тож вона стає параметром шаблона:
// `cpacr::set(bits::cp10_cp11_full)` не дає ні переплутати адресу з даними, ні
// випадково прочитати регістр не тим розміром. Згенерований код той самий, що
// й у макроса CM_REG32 з версії мовою C, — уся різниця з'їдається інлайном.
//
// Адреси й розкладка бітів — з ARMv7-M Architecture Reference Manual, B3.2.

#pragma once

#include <cstdint>

namespace mcu {

template <std::uintptr_t Address>
class Register {
public:
    static std::uint32_t load() noexcept { return *pointer(); }
    static void store(std::uint32_t value) noexcept { *pointer() = value; }
    static void set(std::uint32_t bits) noexcept { store(load() | bits); }

    // Ознаки збою «липкі»: скидаються записом одиниць у ті самі біти.
    static void clear_sticky(std::uint32_t bits) noexcept { store(bits); }

private:
    static volatile std::uint32_t* pointer() noexcept
    {
        return reinterpret_cast<volatile std::uint32_t*>(Address);
    }
};

using icsr  = Register<0xE000ED04>;  // номер активного винятку
using vtor  = Register<0xE000ED08>;  // адреса векторної таблиці
using ccr   = Register<0xE000ED14>;  // поведінка ядра
using shcsr = Register<0xE000ED24>;  // дозвіл окремих обробників збоїв
using cfsr  = Register<0xE000ED28>;  // причина MemManage / BusFault / UsageFault
using hfsr  = Register<0xE000ED2C>;  // причина HardFault
using mmfar = Register<0xE000ED34>;  // адреса, що порушила захист MPU
using bfar  = Register<0xE000ED38>;  // адреса, на якій відмовила шина
using cpacr = Register<0xE000ED88>;  // доступ до співпроцесорів (FPU)

namespace bits {

// CPACR: повний доступ до CP10 і CP11 — обидва блоки FPU, по два біти на кожен.
inline constexpr std::uint32_t cp10_cp11_full = 0xFu << 20;

// SHCSR: доки біт не виставлено, ядро ескалює відповідний збій у HardFault.
inline constexpr std::uint32_t memfault_enable = 1u << 16;
inline constexpr std::uint32_t busfault_enable = 1u << 17;
inline constexpr std::uint32_t usgfault_enable = 1u << 18;

// CCR: пастка на ділення цілого на нуль.
inline constexpr std::uint32_t div_0_trap = 1u << 4;

// ICSR: молодші дев'ять бітів — номер винятку, що виконується просто зараз.
inline constexpr std::uint32_t vectactive_mask = 0x1FFu;

// EXC_RETURN: біт 2 каже, на якому стеку ядро лишило кадр винятку.
inline constexpr std::uint32_t exc_return_psp = 1u << 2;

}  // namespace bits

// ── Інструкції, яких у мові немає ────────────────────────────────────────────

inline void dsb() noexcept { __asm volatile("dsb 0xF" ::: "memory"); }
inline void isb() noexcept { __asm volatile("isb 0xF" ::: "memory"); }
inline void wait_for_interrupt() noexcept { __asm volatile("wfi" ::: "memory"); }
inline void breakpoint() noexcept { __asm volatile("bkpt #0"); }

inline std::uint32_t main_stack_pointer() noexcept
{
    std::uint32_t value;
    __asm volatile("mrs %0, msp" : "=r"(value));
    return value;
}

inline std::uint32_t active_exception() noexcept
{
    return icsr::load() & bits::vectactive_mask;
}

// Термінальна пастка: під налагоджувачем ядро спиняється тут, без нього —
// спить до наступного переривання, не гріючи чіп.
[[noreturn]] inline void halt() noexcept
{
    breakpoint();
    for (;;) {
        wait_for_interrupt();
    }
}

}  // namespace mcu
