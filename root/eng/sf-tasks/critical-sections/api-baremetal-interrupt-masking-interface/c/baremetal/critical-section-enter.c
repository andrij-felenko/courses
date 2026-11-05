#include <stdint.h>
#include "core_cm4.h"

// Структура даних для збереження стану критичної секції
typedef struct {
    uint32_t primask_state;
} critical_section_t;

// Вхід у критичну секцію із збереженням стану
static inline critical_section_t critical_section_enter(void) {
    critical_section_t cs;
    cs.primask_state = __get_PRIMASK();
    __disable_irq();
    // Бар'єр пам'яті для запобігання переупорядкуванню компілятором
    __asm__ __volatile__("" ::: "memory");
    return cs;
}

// Вихід з критичної секції з відновленням стану
static inline void critical_section_exit(critical_section_t cs) {
    __asm__ __volatile__("" ::: "memory");
    __set_PRIMASK(cs.primask_state);
}

// Приклад безпечного оновлення системного буфера
void safe_buffer_update(uint32_t *buffer, uint32_t data) {
    critical_section_t cs = critical_section_enter();
    buffer[0] = data;
    buffer[1] = ~data;
    critical_section_exit(cs);
}
