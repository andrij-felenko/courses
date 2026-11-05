#include <stdint.h>
#include <stdbool.h>

#define MAX_ALLOWED_CYCLES 500U

// Програмна відлагоджувальна обгортка критичної секції
typedef struct {
    uint32_t saved_state;
    uint32_t start_cycles;
} debug_critical_section_t;

static inline void debug_critical_enter(debug_critical_section_t *cs) {
    cs->start_cycles = DWT->CYCCNT; // Фіксація початкового такту
    cs->saved_state = critical_section_enter();
    GPIOB->BSRR = (1U << 5); // Встановлення GPIO пина в 1 для трасування
}

static inline void debug_critical_exit(debug_critical_section_t *cs) {
    GPIOB->BSRR = (1U << (5 + 16)); // Скидання GPIO пина в 0
    critical_section_exit(cs->saved_state);
    
    uint32_t elapsed = DWT->CYCCNT - cs->start_cycles;
    if (elapsed > MAX_ALLOWED_CYCLES) {
        // Перевищення максимально допустимої тривалості — виклик діагностики
        on_critical_section_timeout_error(elapsed);
    }
}
