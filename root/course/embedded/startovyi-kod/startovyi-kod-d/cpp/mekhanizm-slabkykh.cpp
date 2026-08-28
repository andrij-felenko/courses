/* Оголошення слабких обробників мовою C++ */
extern "C" {
    void Default_Handler() {
        while (true) {
        }
    }

    void NMI_Handler()        __attribute__((weak, alias("Default_Handler")));
    void HardFault_Handler()  __attribute__((weak, alias("Default_Handler")));
    void SysTick_Handler()    __attribute__((weak, alias("Default_Handler")));
    void USART1_IRQHandler()  __attribute__((weak, alias("Default_Handler")));
}
