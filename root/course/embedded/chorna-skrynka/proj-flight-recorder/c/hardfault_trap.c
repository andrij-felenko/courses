/* hardfault_trap.c - Апаратний перехоплювач винятків ARM Cortex-M (C) */
#include "flight_recorder_core.h"

void prvGetRegistersFromStack(uint32_t* pulFaultStackAddress) {
    /* Регістри апаратного стекового кадру */
    uint32_t r0  = pulFaultStackAddress[0];
    uint32_t r1  = pulFaultStackAddress[1];
    uint32_t r2  = pulFaultStackAddress[2];
    uint32_t r3  = pulFaultStackAddress[3];
    uint32_t r12 = pulFaultStackAddress[4];
    uint32_t lr  = pulFaultStackAddress[5]; /* Адреса повернення */
    uint32_t pc  = pulFaultStackAddress[6]; /* Адреса інструкції збою */
    uint32_t psr = pulFaultStackAddress[7];

    /* Регістри конфігурації збоїв Cortex-M (CFSR, HFSR, MMFAR, BFAR) */
    volatile uint32_t cfsr = (*((volatile uint32_t*)0xE000ED28));
    volatile uint32_t bfar = (*((volatile uint32_t*)0xE000ED38));

    /* Фіксація аварії в чорній скриньці */
    blackbox_emergency_panic((uint8_t)(cfsr & 0xFF), pc, bfar);

    /* Програмне перезавантаження ядра для виходу з аварійного стану */
    volatile uint32_t* aircr = (volatile uint32_t*)0xE000ED0C;
    *aircr = 0x05FA0000U | (1U << 2); /* NVIC_SystemReset */
    while (1) { __asm volatile("nop"); }
}

/* Асемблерний перехоплювач: вибирає MSP або PSP залежно від EXC_RETURN */
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "b prvGetRegistersFromStack\n"
    );
}
