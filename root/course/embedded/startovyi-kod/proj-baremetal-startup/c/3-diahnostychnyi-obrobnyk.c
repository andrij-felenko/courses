/* Діагностичний аналізатор збою HardFault мовою C */
void HardFault_Handler_C(uint32_t *stack_frame) {
    volatile uint32_t r0  = stack_frame[0];
    volatile uint32_t r1  = stack_frame[1];
    volatile uint32_t r2  = stack_frame[2];
    volatile uint32_t r3  = stack_frame[3];
    volatile uint32_t r12 = stack_frame[4];
    volatile uint32_t lr  = stack_frame[5];
    volatile uint32_t pc  = stack_frame[6]; /* Адреса інструкції, що викликала збій */
    volatile uint32_t psr = stack_frame[7];

    volatile uint32_t cfsr = *(volatile uint32_t *)0xE000ED28;
    volatile uint32_t hfsr = *(volatile uint32_t *)0xE000ED2C;

    (void)r0; (void)r1; (void)r2; (void)r3; (void)r12; (void)lr; (void)pc; (void)psr;
    (void)cfsr; (void)hfsr;

    /* Зупинка під налагоджувачем */
    __asm volatile("bkpt #0");
    while (1) {
    }
}
