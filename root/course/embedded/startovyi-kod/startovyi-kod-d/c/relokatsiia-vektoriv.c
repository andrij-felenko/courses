/* Перенесення таблиці векторів на нову адресу у Flash або RAM */
void relocate_vector_table(uint32_t new_vector_base_address) {
    volatile uint32_t *scb_vtor = (volatile uint32_t *)0xE000ED08UL;
    
    /* Нова адреса має бути строго вирівняна по ступеню двійки (мінімум 128 або 512 байт) */
    *scb_vtor = new_vector_base_address;
    
    /* Бар'єри пам'яті гарантують завершення операції запису до наступного переривання */
    __asm volatile("dsb\n\tisb" ::: "memory");
}
