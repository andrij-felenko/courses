// critical_section.hpp — маскування переривань як RAII-об'єкт.
//
// 64-розрядний накопичувач на 32-розрядному ядрі оновлюється двома
// інструкціями, тож і оновлення, і читання статистики мають бути неподільні.
// Замість парних cpsid/cpsie у кожній гілці — область видимості: вихід
// будь-яким шляхом (return, виняток) відновлює попередній стан PRIMASK.
#pragma once

#include <cstdint>

namespace cortex {

class CriticalSection {
public:
    CriticalSection() noexcept : primask_{read_primask()}
    {
        __asm__ volatile("cpsid i" ::: "memory");
    }

    ~CriticalSection() noexcept
    {
        if ((primask_ & 1U) == 0U) { // переривання були дозволені — вертаємо
            __asm__ volatile("cpsie i" ::: "memory");
        }
    }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;

private:
    [[nodiscard]] static std::uint32_t read_primask() noexcept
    {
        std::uint32_t value;
        __asm__ volatile("mrs %0, primask" : "=r"(value));
        return value;
    }

    std::uint32_t primask_;
};

} // namespace cortex
