/* Асемблерний перехоплювач винятку HardFault для Cortex-M (C++) */
extern "C" [[gnu::naked]] void HardFault_Handler() noexcept {
    __asm volatile (
        " tst lr, #4            \n" /* Перевірка біта 2 регістра LR (EXC_RETURN) */
        " ite eq                \n"
        " mrseq r0, msp         \n" /* Якщо біт 0: стек-фрейм лежить у MSP */
        " mrsne r0, psp         \n" /* Якщо біт 1: стек-фрейм лежить у PSP */
        " mov r1, lr            \n" /* Передаємо значення EXC_RETURN другим аргументом */
        " b prv_hardfault_c_handler \n" /* Перехід до C++ обробника */
    );
}
