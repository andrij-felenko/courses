#include <cstdint>

class DebugCriticalSectionGuard {
public:
    explicit DebugCriticalSectionGuard(std::uint32_t max_cycles = 500U) noexcept
        : m_max_cycles(max_cycles)
    {
        m_start_cycles = DWT->CYCCNT;
        __asm__ volatile (
            "MRS %0, primask\n\t"
            "CPSID i\n\t"
            : "=r" (m_saved_state)
            :: "memory"
        );
        // Фізичне трасування через GPIO пин
        GPIOB->BSRR = (1U << 5);
    }

    ~DebugCriticalSectionGuard() noexcept {
        GPIOB->BSRR = (1U << (5 + 16));
        __asm__ volatile ("dmb" ::: "memory");
        __asm__ volatile (
            "MSR primask, %0\n\t"
            :: "r" (m_saved_state)
            : "memory"
        );

        std::uint32_t elapsed = DWT->CYCCNT - m_start_cycles;
        if (elapsed > m_max_cycles) {
            on_timeout_error(elapsed);
        }
    }

    DebugCriticalSectionGuard(const DebugCriticalSectionGuard&) = delete;
    DebugCriticalSectionGuard& operator=(const DebugCriticalSectionGuard&) = delete;

private:
    std::uint32_t m_saved_state;
    std::uint32_t m_start_cycles;
    std::uint32_t m_max_cycles;

    static void on_timeout_error(std::uint32_t elapsed_cycles) {
        // Асерт або запис системної помилки в журнал
        (void)elapsed_cycles;
    }
};
