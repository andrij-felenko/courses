#include <cstdint>
#include "core_cm4.h"

// C++ RAII Guard з автоматичною діагностикою часових затримок
template <uint32_t MaxCycles = 500U>
class [[nodiscard]] DiagnosticCriticalGuard {
public:
    DiagnosticCriticalGuard() noexcept 
        : m_saved_primask(__get_PRIMASK()),
          m_start_cycles(DWT->CYCCNT) {
        __disable_irq();
        __DSB();
        __ISB();
    }

    ~DiagnosticCriticalGuard() noexcept {
        uint32_t elapsed = DWT->CYCCNT - m_start_cycles;
        __DSB();
        __set_PRIMASK(m_saved_primask);
        __ISB();

        if (elapsed > MaxCycles) {
            on_threshold_exceeded(elapsed);
        }
    }

    DiagnosticCriticalGuard(const DiagnosticCriticalGuard&) = delete;
    DiagnosticCriticalGuard& operator=(const DiagnosticCriticalGuard&) = delete;

private:
    uint32_t m_saved_primask;
    uint32_t m_start_cycles;

    void on_threshold_exceeded(uint32_t elapsed) noexcept {
        // Обробити ситуацію перевищення ліміту часу (наприклад, викликом тригера відлагодження)
        (void)elapsed;
        asm volatile ("bkpt #1");
    }
};

// Приклад безпечного використання діагностичного об'єкта
void safe_telemetry_update(uint32_t &value) {
    DiagnosticCriticalGuard<300U> guard; // Максимум 300 тактів для цієї операції
    value += 42U;
}
