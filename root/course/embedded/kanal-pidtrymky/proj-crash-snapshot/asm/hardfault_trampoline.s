/* hardfault_trampoline.s */
.syntax unified
.thumb
.global HardFault_Handler

HardFault_Handler:
    TST LR, #4               /* Перевірка біта 2 регістра LR (EXC_RETURN) */
    ITE EQ
    MRSEQ R0, MSP            /* Якщо 0 — активний Main Stack Pointer */
    MRSNE R0, PSP            /* Якщо 1 — активний Process Stack Pointer */
    B HardFault_Handler_C    /* Перехід у C/C++ обробник із вказівником у R0 */
