#include <stdint.h>

// Базові визначення регістрів для ARM Cortex-M та RISC-V
#if defined(__ARM_ARCH)
#include "core_cm4.h"
#elif defined(__riscv)
#include <riscv_encoding.h>
#endif

typedef struct {
    uint32_t saved_mask;
} critical_section_t;

// Вхід у критичну секцію з повним апаратним бар'єром
static inline critical_section_t critical_section_enter(void) {
    critical_section_t cs;
#if defined(__ARM_ARCH)
    cs.saved_mask = __get_PRIMASK();
    __disable_irq();
    __DSB();
    __ISB();
#elif defined(__riscv)
    // Зчитати та очистити біт MIE в регістрі mstatus
    cs.saved_mask = __read_and_clear_mstatus_mie();
    __asm__ __volatile__("fence" ::: "memory");
#else
    #error "Непідтримувана апаратна архітектура"
#endif
    return cs;
}

// Вихід з критичної секції з відновленням апаратного стану
static inline void critical_section_exit(critical_section_t cs) {
#if defined(__ARM_ARCH)
    __DSB();
    __set_PRIMASK(cs.saved_mask);
    __ISB();
#elif defined(__riscv)
    __asm__ __volatile__("fence" ::: "memory");
    __restore_mstatus_mie(cs.saved_mask);
#endif
}

// Приклад безпечного атомарного оновлення конфігурації периферії
void hardware_register_update(volatile uint32_t *reg, uint32_t mask, uint32_t val) {
    critical_section_t cs = critical_section_enter();
    uint32_t current = *reg;
    current &= ~mask;
    current |= (val & mask);
    *reg = current;
    critical_section_exit(cs);
}
