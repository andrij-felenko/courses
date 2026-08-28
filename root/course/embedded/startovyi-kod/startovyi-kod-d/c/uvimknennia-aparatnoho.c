/* Увімкнення FPU у стартовому коді */
void enable_fpu_coprocessor(void) {
    volatile uint32_t *scb_cpacr = (volatile uint32_t *)0xE000ED88UL;
    
    /* Встановлюємо біти 20..23 у значення 0b1111 (0xF) */
    *scb_cpacr |= (0xFUL << 20);
    
    /* Інструкції синхронізації шин і конвеєра */
    __asm volatile("dsb\n\tisb" ::: "memory");
}
