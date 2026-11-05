#include <stdint.h>

// Зчитування та вимикання переривань із збереженням попереднього стану
static inline uint32_t critical_section_enter(void) {
    uint32_t primask_state;
    // Зчитуємо поточний стан PRIMASK та вимикаємо переривання
    __asm__ volatile (
        "MRS %0, primask\n\t"
        "CPSID i\n\t"
        : "=r" (primask_state)
        :: "memory"
    );
    return primask_state;
}

// Відновлення попереднього стану переривань
static inline void critical_section_exit(uint32_t saved_state) {
    // Апаратний бар'єр пам'яті для завершення всіх операцій запису
    __asm__ volatile ("dmb" ::: "memory");
    
    // Відновлення значення PRIMASK
    __asm__ volatile (
        "MSR primask, %0\n\t"
        :: "r" (saved_state)
        : "memory"
    );
}

// Приклад використання в C
void update_shared_hardware_counter(volatile uint32_t *counter) {
    uint32_t state = critical_section_enter();
    *counter = *counter + 1; // Атомарне оновлення лічильника
    critical_section_exit(state);
}
