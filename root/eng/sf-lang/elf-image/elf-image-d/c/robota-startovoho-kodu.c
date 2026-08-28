#include <stdint.h>
#include <stddef.h>

/* Символи експортуються лінкер-скриптом.
   Вони не є змінними, їхні АДРЕСИ позначають межі областей пам'яті! */
extern uint32_t _sidata; /* LMA: Початок початкових даних .data у Flash */
extern uint32_t _sdata;  /* VMA: Початок секції .data в SRAM */
extern uint32_t _edata;  /* VMA: Кінець секції .data в SRAM */
extern uint32_t _sbss;   /* VMA: Початок секції .bss в SRAM */
extern uint32_t _ebss;   /* VMA: Кінець секції .bss в SRAM */

void SystemInit(void);
int main(void);

void Reset_Handler_C(void) {
    /* 1. Копіювання ініціалізованих змінних (.data) з Flash у RAM */
    uint32_t *p_src = &_sidata;
    uint32_t *p_dst = &_sdata;

    while (p_dst < &_edata) {
        *p_dst++ = *p_src++;
    }

    /* 2. Обнулення неініціалізованих змінних (.bss) у RAM */
    uint32_t *p_bss = &_sbss;
    while (p_bss < &_ebss) {
        *p_bss++ = 0;
    }

    /* 3. Базове налаштування тактування процесора */
    SystemInit();

    /* 4. Перехід до виконання користувацького коду */
    (void)main();

    /* Захисний нескінченний цикл на випадок виходу з main() */
    while (1) {
    }
}
