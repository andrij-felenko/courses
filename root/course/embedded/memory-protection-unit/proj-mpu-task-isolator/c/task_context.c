#include "task_context.h"
#include <string.h>

#define INITIAL_XPSR_THUMB_BIT  (0x01000000UL) /* Обов'язковий Thumb-режим для Cortex-M */

/* Функція-заглушка завершення задачі при поверненні з entry */
static void task_exit_trap(void) {
    /* Непривілейована задача завершилась — викликаємо системний виклик зупинки */
    task_syscall(0xFFU, 0, 0);
    while (1) {
        /* Якщо ядро не перемкнуло контекст, зациклюємось */
    }
}

/* Ініціалізація початкового стек-фрейму задачі */
void task_create_context(task_control_block_t *tcb,
                         task_entry_fn         entry,
                         void                 *arg,
                         uint32_t             *stack_buffer,
                         uint32_t              stack_size_bytes,
                         uint32_t              guard_size_bytes,
                         const char           *name) {
    if (!tcb || !entry || !stack_buffer || stack_size_bytes <= guard_size_bytes) {
        return;
    }

    memset(tcb, 0, sizeof(task_control_block_t));
    tcb->task_name = name ? name : "task_unnamed";
    tcb->is_privileged = false;
    tcb->is_active = true;

    /* Налаштування дескриптора ізоляції MPU */
    tcb->isolation_desc.task_id = (uint32_t)(uintptr_t)tcb;
    tcb->isolation_desc.stack_base = (uint32_t)(uintptr_t)stack_buffer;
    tcb->isolation_desc.stack_size = stack_size_bytes;
    tcb->isolation_desc.guard_size = guard_size_bytes;
    tcb->isolation_desc.private_data_base = 0U;
    tcb->isolation_desc.private_data_size = 0U;

    /*
     * Формуємо початковий стек. Cortex-M стек росте вниз (Full-Descending).
     * Верхівка стека — найвища адреса, вирівняна на 8 байтів за вимогою AAPCS.
     */
    uint32_t *sp = (uint32_t *)((uintptr_t)stack_buffer + stack_size_bytes);
    sp = (uint32_t *)((uintptr_t)sp & ~0x7UL);

    /*
     * Регістри апаратного стек-фрейму (зберігаються CPU при виклику/перериванні):
     * xPSR, PC, LR, R12, R3, R2, R1, R0
     */
    *(--sp) = INITIAL_XPSR_THUMB_BIT;      /* xPSR: встановлений біт T (Thumb) */
    *(--sp) = (uint32_t)(uintptr_t)entry;  /* PC: адреса функції задачі */
    *(--sp) = (uint32_t)(uintptr_t)task_exit_trap; /* LR: адреса завершення */
    *(--sp) = 0x12121212UL;                /* R12 */
    *(--sp) = 0x03030303UL;                /* R3 */
    *(--sp) = 0x02020202UL;                /* R2 */
    *(--sp) = 0x01010101UL;                /* R1 */
    *(--sp) = (uint32_t)(uintptr_t)arg;    /* R0: перший аргумент функції задачі */

    /*
     * Програмно збережені регістри планувальника RTOS (R4-R11):
     */
    *(--sp) = 0x11111111UL;                /* R11 */
    *(--sp) = 0x10101010UL;                /* R10 */
    *(--sp) = 0x09090909UL;                /* R9 */
    *(--sp) = 0x08080808UL;                /* R8 */
    *(--sp) = 0x07070707UL;                /* R7 */
    *(--sp) = 0x06060606UL;                /* R6 */
    *(--sp) = 0x05050505UL;                /* R5 */
    *(--sp) = 0x04040404UL;                /* R4 */

    tcb->stack_top = sp;
}

/* Скидання привілеїв у регістрі CONTROL процесора (CONTROL.nPRIV = 1) */
void task_drop_privileges(void) {
#if defined(__GNUC__) || defined(__clang__)
    __asm volatile(
        "mrs r0, control   \n"
        "orr r0, r0, #1    \n" /* nPRIV біт = 1 (Unprivileged) */
        "msr control, r0   \n"
        "isb               \n"
        ::: "r0", "memory"
    );
#endif
}

/* Системний виклик через інструкцію SVC */
uint32_t task_syscall(uint32_t svc_number, uint32_t param1, uint32_t param2) {
    uint32_t result = 0;
#if defined(__GNUC__) || defined(__clang__)
    register uint32_t r0 __asm("r0") = svc_number;
    register uint32_t r1 __asm("r1") = param1;
    register uint32_t r2 __asm("r2") = param2;

    __asm volatile(
        "svc 0             \n"
        : "=r"(r0)
        : "r"(r0), "r"(r1), "r"(r2)
        : "memory"
    );
    result = r0;
#else
    (void)svc_number;
    (void)param1;
    (void)param2;
#endif
    return result;
}
