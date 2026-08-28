// Точка входу: визначаємо активний стек і передаємо його у C-обробник
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4            \n"  // біт 2 EXC_RETURN: який стек?
        "ite eq               \n"
        "mrseq r0, msp        \n"  // біт = 0 → кадр на MSP
        "mrsne r0, psp        \n"  // біт = 1 → кадр на PSP
        "b hardfault_report   \n"  // r0 = покажчик на кадр
    );
}
