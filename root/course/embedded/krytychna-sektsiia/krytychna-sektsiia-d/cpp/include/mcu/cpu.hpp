// Доступ до регістрів стану ядра Cortex-M. У бойовій прошивці ці інструкції
// дає CMSIS; тут вони виписані, щоб було видно, у що саме перетворюється виклик,
// і щоб приклад збирався без усього дерева CMSIS.
#pragma once

#include <cstdint>

#ifndef __NVIC_PRIO_BITS
#define __NVIC_PRIO_BITS 4U // у справжній прошивці приходить з device-заголовка
#endif

namespace mcu::cpu {

#if defined(__ARM_ARCH_6M__)
inline constexpr bool kHasBasepri = false;   // Cortex-M0/M0+ маскує лише все одразу
inline constexpr bool kHasExclusive = false; // і не має монітора ексклюзивності
#else
inline constexpr bool kHasBasepri = true;
inline constexpr bool kHasExclusive = true;
#endif

inline constexpr std::uint32_t kNvicPrioBits = __NVIC_PRIO_BITS;

// Барʼєр компілятора: доступи до памʼяті не переїжджають через цю межу.
[[gnu::always_inline]] inline void barrier() noexcept { __asm volatile("" ::: "memory"); }

// Апаратний барʼєр — для другого ядра й DMA, а не для оптимізатора.
inline void dmb() noexcept { __asm volatile("DMB 0xF" ::: "memory"); }

[[nodiscard]] inline std::uint32_t primask() noexcept
{
    std::uint32_t value;
    __asm volatile("MRS %0, primask" : "=r"(value)::"memory");
    return value;
}

inline void set_primask(std::uint32_t value) noexcept
{
    __asm volatile("MSR primask, %0" ::"r"(value) : "memory");
}

inline void disable_irq() noexcept { __asm volatile("CPSID i" ::: "memory"); }
inline void enable_irq() noexcept { __asm volatile("CPSIE i" ::: "memory"); }

#if !defined(__ARM_ARCH_6M__)
[[nodiscard]] inline std::uint32_t basepri() noexcept
{
    std::uint32_t value;
    __asm volatile("MRS %0, basepri" : "=r"(value)::"memory");
    return value;
}

inline void set_basepri(std::uint32_t value) noexcept
{
    __asm volatile("MSR basepri, %0" ::"r"(value) : "memory");
}

// MSR basepri_max опускає поріг, лише якщо новий суворіший за чинний, — тому
// вкладена секція не може випадково послабити зовнішню.
inline void set_basepri_max(std::uint32_t value) noexcept
{
    __asm volatile("MSR basepri_max, %0" ::"r"(value) : "memory");
}
#endif

} // namespace mcu::cpu
