#include <cstdint>
#include <atomic>
#include "core_cm4.h"

// RAII-клас для автоматичного захисту критичної секції
class CriticalSectionGuard {
public:
    CriticalSectionGuard() noexcept 
        : m_primask(__get_PRIMASK()) {
        __disable_irq();
        std::atomic_signal_fence(std::memory_order_seq_cst);
    }

    ~CriticalSectionGuard() noexcept {
        std::atomic_signal_fence(std::memory_order_seq_cst);
        __set_PRIMASK(m_primask);
    }

    // Заборона копіювання та переміщення об'єкта
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard(CriticalSectionGuard&&) = delete;
    CriticalSectionGuard& operator=(CriticalSectionGuard&&) = delete;

private:
    uint32_t m_primask;
};

// Приклад використання RAII в об'єктно-орієнтованому коді
void safe_buffer_update_cpp(uint32_t *buffer, uint32_t data) {
    CriticalSectionGuard lock;
    buffer[0] = data;
    buffer[1] = ~data;
    // Деструктор lock автоматично відновить PRIMASK при виході
}
