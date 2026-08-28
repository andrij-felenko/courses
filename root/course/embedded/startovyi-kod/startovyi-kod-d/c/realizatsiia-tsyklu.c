/* Класична реалізація ініціалізації пам'яті мовою C */
extern uint32_t _sidata; /* Початок початкових значень .data у Flash (LMA) */
extern uint32_t _sdata;  /* Початок секції .data в RAM (VMA) */
extern uint32_t _edata;  /* Кінець секції .data в RAM (VMA) */
extern uint32_t _sbss;   /* Початок секції .bss в RAM (VMA) */
extern uint32_t _ebss;   /* Кінець секції .bss в RAM (VMA) */

void init_memory_sections(void) {
    /* 1. Копіювання секції .data з Flash у RAM */
    uint32_t *p_src = &_sidata;
    uint32_t *p_dst = &_sdata;
    while (p_dst < &_edata) {
        *p_dst++ = *p_src++;
    }

    /* 2. Заповнення секції .bss нулями в RAM */
    uint32_t *p_bss = &_sbss;
    while (p_bss < &_ebss) {
        *p_bss++ = 0;
    }
}
