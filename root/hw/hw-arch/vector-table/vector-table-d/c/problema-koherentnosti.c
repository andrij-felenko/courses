/* Протокол безпечного оновлення вектора в кешованій пам'яті RAM */
void update_ram_vector_safe(uint32_t irq_num, isr_fn new_handler) {
    /* 1. Запис нової адреси в масив таблиці */
    sram_vector_table[16 + irq_num] = new_handler;

    /* 2. Скидання (Clean) лінії D-Cache у фізичну пам'ять SRAM */
    uint32_t *target_addr = (uint32_t*)&sram_vector_table[16 + irq_num];
    SCB_CleanDCache_by_Addr(target_addr, sizeof(uint32_t));

    /* 3. Знедійнення (Invalidate) кешу інструкцій I-Cache */
    SCB_InvalidateICache();

    /* 4. Бар'єри пам'яті та конвеєра */
    __DSB();
    __ISB();
}
