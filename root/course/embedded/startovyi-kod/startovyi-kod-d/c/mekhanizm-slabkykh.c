/* Оголошення слабких обробників переривань */
void Default_Handler(void) {
    /* Нескінченна пастка: якщо ми потрапили сюди, переривання було
       увімкнено в NVIC, але для нього не написали реальний обробник */
    while (1) {
    }
}

void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));
void USART1_IRQHandler(void)  __attribute__((weak, alias("Default_Handler")));
