/* core/src/startup_stm32f407xx.c */
#include <stdint.h>

/* Символи, експортовані скриптом компонування GNU LD */
extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

extern void SystemInit(void);
extern void __libc_init_array(void);
extern int main(void);

void Reset_Handler(void);
void Default_Handler(void) {
    while (1) {}
}

/* Оголошення переривань як weak-аліасів до Default_Handler */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Таблиця векторів переривань */
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))((uint32_t)&_estack), /* 0x00: Початкове значення SP */
    Reset_Handler,                         /* 0x04: Скидання (Reset) */
    NMI_Handler,                           /* 0x08: NMI */
    HardFault_Handler,                     /* 0x0C: Hard Fault */
    0, 0, 0, 0, 0, 0, 0,                   /* Зарезервовано */
    0, 0, 0,                               /* SVC, DebugMon, PendSV */
    SysTick_Handler,                       /* 0x3C: SysTick */
};

void Reset_Handler(void) {
    /* 1. Копіювання ініціалізованих даних з Flash у RAM */
    uint32_t *pSrc = &_sidata;
    uint32_t *pDst = &_sdata;
    while (pDst < &_edata) {
        *pDst++ = *pSrc++;
    }

    /* 2. Обнулення неініціалізованої пам'яті BSS */
    pDst = &_sbss;
    while (pDst < &_ebss) {
        *pDst++ = 0;
    }

    /* 3. Ініціалізація апаратної підсистеми тактування */
    SystemInit();

    /* 4. Виклик конструкторів глобальних C++ об'єктів */
    __libc_init_array();

    /* 5. Перехід до основної програми */
    main();

    /* Якщо main() завершився — зупиняємось у нескінченному циклі */
    while (1) {}
}
