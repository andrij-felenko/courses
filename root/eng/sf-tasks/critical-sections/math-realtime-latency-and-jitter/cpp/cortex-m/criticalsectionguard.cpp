#include <cstdint>

class CriticalSectionGuard {
public:
    // Конструктор зберігає стан та маскує переривання (RAII)
    CriticalSectionGuard() noexcept {
        __asm__ volatile (
            "MRS %0, primask\n\t"
            "CPSID i\n\t"
            : "=r" (m_saved_state)
            :: "memory"
        );
    }

    // Деструктор автоматично відновлює стан при виході зі скоупу
    ~CriticalSectionGuard() noexcept {
        __asm__ volatile ("dmb" ::: "memory");
        __asm__ volatile (
            "MSR primask, %0\n\t"
            :: "r" (m_saved_state)
            : "memory"
        );
    }

    // Заборона копіювання для безпеки
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;

private:
    std::uint32_t m_saved_state;
};

// Приклад використання в C++
void safe_buffer_append(volatile uint32_t &shared_var, uint32_t value) {
    CriticalSectionGuard guard;
    shared_var += value; // Безпечне атомарне додавання
}
