// startup_cortexm.c — типовий стартовий файл на C99 з таблицею векторів
#include <stdint.h>

// Оголошення типів покажчиків на обробники
typedef void (*isr_handler_t)(void);

// Зовнішні символи з лінкер-скрипта
extern uint32_t _estack;
extern void Reset_Handler(void);

// Єдина універсальна пастка для непередбачених переривань
void Default_Handler(void)
{
    // Якщо програма потрапила сюди, спрацювало апаратне переривання,
    // для якого розробник не написав власного обробника.
    while (1) {
        // Пастка
    }
}

// Оголошення слабких псевдонімів для системних та периферійних переривань
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));
void USART1_IRQHandler(void)  __attribute__((weak, alias("Default_Handler")));
void TIM2_IRQHandler(void)    __attribute__((weak, alias("Default_Handler")));

// Таблиця векторів розміщується у спеціальній секції .isr_vector
__attribute__((section(".isr_vector"), used))
const isr_handler_t g_vector_table[] = {
    (isr_handler_t)&_estack,      // Початкова вершина стека
    Reset_Handler,                // Точка входу процесора
    NMI_Handler,                  // Non-Maskable Interrupt
    HardFault_Handler,            // Апаратна аварія
    0, 0, 0, 0, 0, 0, 0,          // Зарезервовано архітектурою ARM
    SysTick_Handler,              // Системний таймер
    USART1_IRQHandler,            // Переривання UART1
    TIM2_IRQHandler               // Переривання таймера TIM2
};
