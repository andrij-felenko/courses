#include "critical_section.h"
#include "FreeRTOS.h"
#include "task.h"

/* Контекстно-незалежний вхід у критичну секцію FreeRTOS */
typedef struct {
    bool is_isr;
    UBaseType_t isr_state;
} rtos_critical_t;

static inline rtos_critical_t rtos_critical_enter(void) {
    rtos_critical_t rc;
    rc.is_isr = in_interrupt_context();
    if (rc.is_isr) {
        rc.isr_state = taskENTER_CRITICAL_FROM_ISR();
    } else {
        taskENTER_CRITICAL();
        rc.isr_state = 0;
    }
    return rc;
}

static inline void rtos_critical_exit(rtos_critical_t rc) {
    if (rc.is_isr) {
        taskEXIT_CRITICAL_FROM_ISR(rc.isr_state);
    } else {
        taskEXIT_CRITICAL();
    }
}
