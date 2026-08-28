// C-частина діагностичного обробника
void HardFault_Decoder_C(const uint32_t *stack_frame, uint32_t exc_return) {
    uint32_t r0  = stack_frame[0];
    uint32_t r1  = stack_frame[1];
    uint32_t r2  = stack_frame[2];
    uint32_t r3  = stack_frame[3];
    uint32_t r12 = stack_frame[4];
    uint32_t lr  = stack_frame[5];
    uint32_t pc  = stack_frame[6]; // АДРЕСА ВИННОЇ ІНСТРУКЦІЇ!
    uint32_t psr = stack_frame[7];

    uint32_t hfsr = SCB->HFSR;
    uint32_t cfsr = SCB->CFSR;
    uint32_t bfar = (cfsr & SCB_CFSR_BFARVALID_Msk) ? SCB->BFAR : 0;
    uint32_t mmfar = (cfsr & SCB_CFSR_MMARVALID_Msk) ? SCB->MMFAR : 0;

    // Тут дані записуються в енергонезалежну пам'ять або передаються в UART
    (void)r0; (void)r1; (void)r2; (void)r3; (void)r12;
    (void)lr; (void)pc; (void)psr; (void)hfsr; (void)bfar; (void)mmfar;

    // Запобігаємо зависанню: скидаємо чип через системний ресет
    NVIC_SystemReset();
}

// Асемблерний вхідний трамплін
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4                \n" // Перевірка біта 2 регістра LR (EXC_RETURN)
        "ite eq                    \n"
        "mrseq r0, msp             \n" // Якщо біт=0 -> кадр на MSP
        "mrsne r0, psp             \n" // Якщо біт=1 -> кадр на PSP
        "mov r1, lr                \n" // R1 = значення EXC_RETURN
        "b HardFault_Decoder_C     \n" // Перехід у C-декодер із аргументами (R0, R1)
    );
}
