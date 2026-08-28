/* startup.c — Стартова ініціалізація пам'яті мовою C */
#include <stdint.h>

/* Символи-маркери, експортовані лінкер-скриптом */
extern uint32_t _sidata;  /* Початок початкових значень .data у Flash (LMA) */
extern uint32_t _sdata;   /* Початок .data у RAM (VMA) */
extern uint32_t _edata;   /* Кінець .data у RAM (VMA) */
extern uint32_t _sbss;    /* Початок .bss у RAM (VMA) */
extern uint32_t _ebss;    /* Кінець .bss у RAM (VMA) */

extern void __libc_init_array(void);
extern int main(void);

void Reset_Handler(void) {
    /* 1. Копіювання ініціалізованих змінних .data з Flash у SRAM */
    uint32_t *src = &_sidata;
    uint32_t *dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    /* 2. Очищення секції .bss (заповнення нулями) */
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0U;
    }

    /* 3. Виклик статичних і глобальних конструкторів C++ */
    __libc_init_array();

    /* 4. Запуск головної логіки застосунку */
    main();

    /* Якщо main() завершився — зупинка процесора */
    while (1) {
        __asm volatile("wfi");
    }
}
