/* fault_handlers.c — «голі» вектори винятків збою.
 *
 * Обробник не має права бути звичайною C-функцією: пролог компілятора
 * зіпсує LR (там лежить EXC_RETURN) і зрушить стек до того, як ми знімемо
 * кадр аварії. Тому кожен вектор — naked-заглушка з трьох інструкцій:
 * вибрати стек за бітом 2 у EXC_RETURN, передати кадр і LR у C-функцію.
 *
 * Хвостовий перехід (b), а не виклик (bl): fault_report_entry не повертається,
 * тож зайвий кадр на й так підозрілому стеку нам не потрібен.
 */
#include "fault_diag.h"

#define FAULT_STUB(vector, source_id)                       \
    __attribute__((naked)) void vector(void)                \
    {                                                       \
        __asm volatile(                                     \
            ".syntax unified               \n"              \
            "tst   lr, #4                  \n" /* біт 2 EXC_RETURN */ \
            "ite   eq                      \n"              \
            "mrseq r0, msp                 \n" /* 0 → кадр на MSP */  \
            "mrsne r0, psp                 \n" /* 1 → кадр на PSP */  \
            "mov   r1, lr                  \n"              \
            "mov   r2, %[src]              \n"              \
            "b     fault_report_entry      \n"              \
            :                                               \
            : [src] "i" (source_id)                         \
            : "r0", "r1", "r2", "memory");                  \
    }

FAULT_STUB(HardFault_Handler,  FAULT_SOURCE_HARD)
FAULT_STUB(MemManage_Handler,  FAULT_SOURCE_MEMMANAGE)
FAULT_STUB(BusFault_Handler,   FAULT_SOURCE_BUS)
FAULT_STUB(UsageFault_Handler, FAULT_SOURCE_USAGE)
