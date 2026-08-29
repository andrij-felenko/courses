#pragma once

#include <cstdint>

namespace at {

/* Вимикання переривань як RAII-об'єкт: жодного шляху виходу з функції, на
   якому переривання лишилися б вимкненими. Потрібне рівно в одному місці —
   навколо індексів черги команд, бо покласти команду може і URC-колбек, і
   переривання таймера.

   Кільцевий буфер прийому в цьому не бере участі взагалі: head пише лише
   DMA, tail — лише парсер. */
class CriticalSection {
public:
    CriticalSection() noexcept : saved_{enter()} {}
    ~CriticalSection() { leave(saved_); }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;

private:
#if defined(__ARM_ARCH) && !defined(AT_PORT_HOST)
    static std::uint32_t enter() noexcept
    {
        std::uint32_t primask;
        __asm volatile("mrs %0, primask" : "=r"(primask));
        __asm volatile("cpsid i" ::: "memory");
        return primask;
    }
    static void leave(std::uint32_t saved) noexcept
    {
        // Відновлюємо попередній стан, а не вмикаємо наосліп: інакше вкладена
        // секція розкрила б зовнішню.
        if ((saved & 1U) == 0U) {
            __asm volatile("cpsie i" ::: "memory");
        }
    }
#else
    static std::uint32_t enter() noexcept { return 0; }
    static void leave(std::uint32_t) noexcept {}
#endif

    std::uint32_t saved_;
};

}  // namespace at
