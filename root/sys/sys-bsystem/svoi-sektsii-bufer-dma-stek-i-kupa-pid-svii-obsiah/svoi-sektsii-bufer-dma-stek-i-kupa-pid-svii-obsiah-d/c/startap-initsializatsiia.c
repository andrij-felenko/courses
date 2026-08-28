#include <stdint.h>

extern uint32_t _sidata; /* Початок образу .data у Flash (LMA) */
extern uint32_t _sdata;  /* Початок .data в RAM (VMA) */
extern uint32_t _edata;  /* Кінець .data в RAM (VMA) */
extern uint32_t _sbss;   /* Початок .bss в RAM (VMA) */
extern uint32_t _ebss;   /* Кінець .bss в RAM (VMA) */

extern void SystemInit(void);
extern void __libc_init_array(void);
extern int main(void);

void Reset_Handler(void) {
    uint32_t *src = &_sidata;
    uint32_t *dst = &_sdata;

    /* Копіювання початкових значень .data з Flash у RAM */
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    /* Обнулення секції .bss */
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0U;
    }

    /* Ініціалізація тактування та базових шин */
    SystemInit();

    /* Виклик глобальних конструкторів середовища C/C++ */
    __libc_init_array();

    /* Перехід до основної логіки */
    main();

    /* Нескінченна пастка на випадок виходу з main */
    while (1) {
    }
}
