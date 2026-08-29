// McuPort.hpp — тонкий шар над апаратурою Cortex-M: регістри, критична секція,
// скидання ядра, чистка кешу даних. Критичну секцію тут тримає об'єкт-охоронець,
// тож жодна гілка виходу не може забути ввімкнути переривання назад.
#pragma once

#include <cstddef>
#include <cstdint>

namespace embedded::mcu {

// Адреси System Control Block закріплені архітектурою ARMv6-M/ARMv7-M.
inline constexpr std::uintptr_t kScbAircr   = 0xE000ED0CU;
inline constexpr std::uintptr_t kScbCfsr    = 0xE000ED28U;
inline constexpr std::uintptr_t kScbHfsr    = 0xE000ED2CU;
inline constexpr std::uintptr_t kScbMmfar   = 0xE000ED34U;
inline constexpr std::uintptr_t kScbBfar    = 0xE000ED38U;
inline constexpr std::uintptr_t kScbDccmvac = 0xE000EF68U;

inline constexpr std::uint32_t kCfsrMmarValid = 1U << 7;
inline constexpr std::uint32_t kCfsrBfarValid = 1U << 15;

// Єдина точка, де в цьому коді живе reinterpret_cast на периферію.
template <typename T = std::uint32_t>
[[nodiscard]] inline volatile T& reg(std::uintptr_t address) noexcept {
    return *reinterpret_cast<volatile T*>(address);
}

// Охоронець критичної секції. Зберігає попередній PRIMASK, бо реєстратор
// викликають і з обробників переривань, де переривання вже вимкнені.
class IrqLock {
public:
    IrqLock() noexcept {
        asm volatile("mrs %0, primask\n\t"
                     "cpsid i"
                     : "=r"(primask_)
                     :
                     : "memory");
    }

    ~IrqLock() {
        asm volatile("msr primask, %0" : : "r"(primask_) : "memory");
    }

    IrqLock(const IrqLock&) = delete;
    IrqLock& operator=(const IrqLock&) = delete;

    // Панічний шлях назад не повертається: маску лишаємо піднятою назавжди.
    void keep_locked() noexcept { primask_ = 1U; }

private:
    std::uint32_t primask_{};
};

[[noreturn]] inline void system_reset() noexcept {
    asm volatile("dsb" ::: "memory");
    reg(kScbAircr) = 0x05FA0000U | (1U << 2); // ключ AIRCR + SYSRESETREQ
    asm volatile("dsb" ::: "memory");
    for (;;) {
        asm volatile("nop");
    }
}

// На Cortex-M7 кадри осідають у кеші даних, і автономний запис у SPI віддав би
// на носій застарілу SRAM. Довжина лінії кешу — 32 байти.
inline void clean_dcache(const void* address, std::size_t size) noexcept {
#if defined(BLACKBOX_HAS_DCACHE)
    const auto start = reinterpret_cast<std::uintptr_t>(address) & ~std::uintptr_t{31};
    const auto end   = reinterpret_cast<std::uintptr_t>(address) + size;
    asm volatile("dsb" ::: "memory");
    for (std::uintptr_t line = start; line < end; line += 32U) {
        reg(kScbDccmvac) = static_cast<std::uint32_t>(line);
    }
    asm volatile("dsb" ::: "memory");
    asm volatile("isb" ::: "memory");
#else
    (void)address;
    (void)size;
#endif
}

// Монотонний час у мілісекундах. Реалізує застосунок поверх SysTick:
// реєстратор системним тиком не володіє, він у нього лише позичає.
[[nodiscard]] std::uint32_t uptime_ms() noexcept;

} // namespace embedded::mcu
