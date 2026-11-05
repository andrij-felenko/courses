#include <stdint.h>
#include <stdbool.h>

// Адреси регістрів модуля DWT для ARM Cortex-M
#define DWT_CTRL    (*(volatile uint32_t*)0xE0001000)
#define DWT_CYCCNT  (*(volatile uint32_t*)0xE0001004)
#define DEMCR       (*(volatile uint32_t*)0xE000EDFC)

// Поріг затримки у тактах (наприклад, 800 тактів = 5 мкс при 160 МГц)
#define LATENCY_THRESHOLD_CYCLES 800U

typedef struct {
    uint32_t saved_mask;
    uint32_t start_cycles;
    const char *file;
    uint32_t line;
} diag_critical_state_t;

// Ініціалізація апаратного лічильника циклів DWT
static inline void dwt_counter_init(void) {
    DEMCR |= (1U << 24);   // Вмикаємо трасування TRCENA
    DWT_CTRL |= (1U << 0);  // Вмикаємо лічильник CYCCNT
}

// Діагностичний вхід у критичну секцію
static inline diag_critical_state_t diag_critical_enter(const char *file, uint32_t line) {
    diag_critical_state_t state;
    state.file = file;
    state.line = line;
    
    __asm__ __volatile__(
        "mrs %0, basepri \n\t"
        "msr basepri, %1 \n\t"
        "isb             \n\t"
        : "=r" (state.saved_mask)
        : "r" (0x20)
        : "memory"
    );
    
    state.start_cycles = DWT_CYCCNT; // Фіксуємо початковий такт
    return state;
}

// Діагностичний вихід із перевіркою часового ліміту
static inline void diag_critical_exit(diag_critical_state_t *state) {
    uint32_t elapsed = DWT_CYCCNT - state->start_cycles;
    
    __asm__ __volatile__(
        "msr basepri, %0 \n\t"
        "isb             \n\t"
        :
        : "r" (state->saved_mask)
        : "memory"
    );
    
    // Якщо тривалість перевищує допустимий поріг, фіксуємо затримку
    if (elapsed > LATENCY_THRESHOLD_CYCLES) {
        // Запис у системний журнал або активація точки зупинки
        (void)state->file;
        (void)state->line;
    }
}

static inline void auto_diag_exit(diag_critical_state_t *state) {
    diag_critical_exit(state);
}

// Макрос автоматичної діагностичної критичної секції
#define DIAG_CRITICAL_SECTION_C() \
    diag_critical_state_t __diag_cs __attribute__((cleanup(auto_diag_exit))) = \
        diag_critical_enter(__FILE__, __LINE__)
