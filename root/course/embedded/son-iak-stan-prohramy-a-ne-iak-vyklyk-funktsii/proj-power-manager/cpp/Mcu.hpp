// Mcu.hpp — тонкий шар над ядром Cortex-M4 і деревом тактування STM32L4.
#pragma once

#include <cstdint>
#include "stm32l4xx.h"

namespace emb::hal {

// Критична секція як ресурс: PRIMASK повертається рівно на межі області
// видимості, скільки б виходів із функції не було.
class CriticalSection {
public:
    CriticalSection() noexcept : m_primask{__get_PRIMASK()} { __disable_irq(); }
    ~CriticalSection() { __set_PRIMASK(m_primask); }

    CriticalSection(const CriticalSection&) = delete;
    CriticalSection& operator=(const CriticalSection&) = delete;

private:
    std::uint32_t m_primask;
};

inline void waitForInterrupt() noexcept
{
    __DSB();
    __WFI();
}

enum class ClockSource : std::uint8_t { Msi, Pll };

class SystemClock {
public:
    static constexpr std::uint32_t PllHz = 80'000'000;
    static constexpr std::uint32_t MsiHz = 4'000'000;

    // Піднімає HSE+PLL після виходу зі STOP. Дві невдалі спроби поспіль
    // означають, що працювати далі нема на чому, — тоді перезапуск.
    [[nodiscard]] static ClockSource restoreAfterStop() noexcept;

    [[nodiscard]] static std::uint32_t faults() noexcept { return s_faults; }

private:
    [[nodiscard]] static bool tryRestore() noexcept;
    static inline std::uint32_t s_faults{0};
};

} // namespace emb::hal
