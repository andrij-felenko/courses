#ifndef CRITICAL_SECTION_H
#define CRITICAL_SECTION_H

#include <stdint.h>
#include <stdbool.h>

#if defined(__ARMCC_VERSION) || defined(__GNUC__)
    #include "cmsis_compiler.h"
#else
    #error "Непідтримуваний компілятор: потрібна підтримка CMSIS intrinsics"
#endif

/*
 * Бар'єр оптимізації компілятора:
 * Забороняє компілятору переставляти операції читання/запису пам'яті
 * через межі критичної секції під час оптимізації (-O2, -O3, -Os).
 */
#define CRITICAL_MEMORY_BARRIER() __asm volatile("" ::: "memory")

/* ========================================================================= */
/* 1. Глобальна критична секція на основі PRIMASK (Cortex-M0/M0+/M3/M4/M7/M33) */
/* ========================================================================= */

typedef struct {
    uint32_t primask_state;
} critical_section_t;

static inline critical_section_t critical_section_enter(void) {
    critical_section_t cs;
    cs.primask_state = __get_PRIMASK();
    __disable_irq();
    CRITICAL_MEMORY_BARRIER();
    return cs;
}

static inline void critical_section_exit(critical_section_t cs) {
    CRITICAL_MEMORY_BARRIER();
    __set_PRIMASK(cs.primask_state);
}

/* ========================================================================= */
/* 2. Пріоритетна критична секція на основі BASEPRI (Cortex-M3/M4/M7/M33)   */
/* ========================================================================= */

#if (__CORTEX_M >= 3U) || defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)

typedef struct {
    uint32_t basepri_state;
} priority_critical_section_t;

/*
 * Вхід у критичну секцію із маскуванням переривань з пріоритетом >= max_syscall_prio.
 * max_syscall_prio має бути попередньо зміщеним у старші біти (наприклад, 0x50 для пріоритету 5 при 4 бітах NVIC).
 */
static inline priority_critical_section_t priority_critical_section_enter(uint8_t max_syscall_prio) {
    priority_critical_section_t pcs;
    pcs.basepri_state = __get_BASEPRI();
    /*
     * __set_BASEPRI_MAX встановлює нове значення лише якщо воно підвищує рівень маскування
     * (тобто задає суворіший поріг, ніж поточний), що запобігає випадковому розмаскуванню.
     */
    __set_BASEPRI_MAX(max_syscall_prio);
    CRITICAL_MEMORY_BARRIER();
    return pcs;
}

static inline void priority_critical_section_exit(priority_critical_section_t pcs) {
    CRITICAL_MEMORY_BARRIER();
    __set_BASEPRI(pcs.basepri_state);
}

#endif /* Cortex-M3+ */

/* ========================================================================= */
/* 3. Діагностика контексту виконання (Thread чи ISR)                        */
/* ========================================================================= */

static inline bool in_interrupt_context(void) {
    return (__get_IPSR() != 0U);
}

#endif /* CRITICAL_SECTION_H */
