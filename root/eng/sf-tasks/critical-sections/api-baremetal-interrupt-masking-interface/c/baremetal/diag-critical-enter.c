#include <stdint.h>
#include <stdbool.h>
#include "core_cm4.h"

// Порогове значення максимальної тривалості критичної секції в тактах процесора
#define MAX_ALLOWED_CRITICAL_CYCLES 500U

typedef struct {
    uint32_t saved_primask;
    uint32_t start_cycles;
} diag_critical_section_t;

// Вхід у діагностичну критичну секцію
static inline diag_critical_section_t diag_critical_enter(void) {
    diag_critical_section_t cs;
    cs.saved_primask = __get_PRIMASK();
    __disable_irq();
    __DSB();
    
    // Зчитування поточного значення лічильника тактів DWT
    cs.start_cycles = DWT->CYCCNT;
    return cs;
}

// Вихід з перевіркою тривалості виконання
static inline void diag_critical_exit(diag_critical_section_t cs) {
    uint32_t elapsed_cycles = DWT->CYCCNT - cs.start_cycles;
    __set_PRIMASK(cs.saved_primask);
    __ISB();
    
    // Якщо тривалість перевищила поріг, зупиняємо систему для відлагодження
    if (elapsed_cycles > MAX_ALLOWED_CRITICAL_CYCLES) {
        // Фіксація аварійної події в системному журналі
        __asm__ __volatile__("bkpt #0");
    }
}

// Приклад використання відлагоджувальної критичної секції
void process_critical_telemetry(uint32_t *sensor_data, uint32_t len) {
    diag_critical_section_t cs = diag_critical_enter();
    for (uint32_t i = 0; i < len; ++i) {
        sensor_data[i] = sensor_data[i] * 2U;
    }
    diag_critical_exit(cs);
}
