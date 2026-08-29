// hal/critical_section.hpp — критична секція як RAII-охоронець.
// Вихід із функції будь-якою гілкою — return, break, виняток — відновлює PRIMASK
// сам; забути ввімкнути переривання назад тут нічим.
#pragma once

#include <cstdint>

namespace hal {

class CriticalSection {
public:
    CriticalSection() noexcept : primask_(enter()) {}
    ~CriticalSection() noexcept { exit(primask_); }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;
    CriticalSection(CriticalSection&&) = delete;
    CriticalSection& operator=(CriticalSection&&) = delete;

private:
    static std::uint32_t enter() noexcept
    {
#if defined(__ARM_ARCH) && defined(__GNUC__)
        std::uint32_t primask{};
        __asm__ volatile("mrs %0, primask" : "=r"(primask)::"memory");
        __asm__ volatile("cpsid i" ::: "memory");
        return primask;
#elif defined(__GNUC__) || defined(__clang__)
        // Хостова збірка: переривань немає, потрібен лише барʼєр компілятора.
        __asm__ volatile("" ::: "memory");
        return 0u;
#else
        return 0u;
#endif
    }

    static void exit(std::uint32_t primask) noexcept
    {
#if defined(__ARM_ARCH) && defined(__GNUC__)
        // Вмикаємо лише те, що було ввімкнене на вході: вкладені секції не мають
        // відпускати переривання достроково.
        if ((primask & 1u) == 0u) {
            __asm__ volatile("cpsie i" ::: "memory");
        }
#elif defined(__GNUC__) || defined(__clang__)
        (void)primask;
        __asm__ volatile("" ::: "memory");
#else
        (void)primask;
#endif
    }

    std::uint32_t primask_;
};

}  // namespace hal
