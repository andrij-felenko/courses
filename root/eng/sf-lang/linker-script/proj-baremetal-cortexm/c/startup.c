/* startup.c — Стартова ініціалізація мікроконтролера мовою C */
#include <stdint.h>

/* Символи, визначені у скрипті компонувача stm32f4.ld */
extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;
extern uint32_t _siccmram;
extern uint32_t _sccmram;
extern uint32_t _eccmram;

/* Прототипи функцій */
void Reset_Handler(void);
void Default_Handler(void);
extern void __libc_init_array(void);
extern int main(void);

/* Оголошення слабких обробників винятків Cortex-M */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Таблиця векторів переривань, що примусово розміщується у .isr_vector */
__attribute__((section(".isr_vector"), used))
const uint32_t* const g_pfnVectors[] = {
    (const uint32_t*)&_estack,          /* 0x0000: Початковий Main Stack Pointer */
    (const uint32_t*)Reset_Handler,     /* 0x0004: Вектор скидання процесора */
    (const uint32_t*)NMI_Handler,       /* 0x0008: Немасковане переривання */
    (const uint32_t*)HardFault_Handler, /* 0x000C: Апаратна помилка */
    (const uint32_t*)MemManage_Handler, /* 0x0010: Помилка MPU */
    (const uint32_t*)BusFault_Handler,  /* 0x0014: Помилка шини */
    (const uint32_t*)UsageFault_Handler,/* 0x0018: Помилка інструкції */
    0, 0, 0, 0,                         /* Зарезервовано ARM */
    0, 0, 0,
    (const uint32_t*)SysTick_Handler    /* 0x003C: Системний таймер */
};

void Reset_Handler(void) {
    /* 1. Копіювання секції .data з Flash у SRAM */
    uint32_t *p_src = &_sidata;
    uint32_t *p_dst = &_sdata;
    while (p_dst < &_edata) {
        *p_dst++ = *p_src++;
    }

    /* 2. Занулення секції .bss в SRAM */
    p_dst = &_sbss;
    while (p_dst < &_ebss) {
        *p_dst++ = 0;
    }

    /* 3. Копіювання секції .ccmram з Flash у CCMRAM (за потреби) */
    p_src = &_siccmram;
    p_dst = &_sccmram;
    while (p_dst < &_eccmram) {
        *p_dst++ = *p_src++;
    }

    /* 4. Виклик конструкторів глобальних об'єктів C++ */
    __libc_init_array();

    /* 5. Запуск головної програми */
    main();

    /* Якщо main() повернув значення — нескінченний цикл */
    while (1) {}
}

void Default_Handler(void) {
    while (1) {}
}
