uint8_t hc165_read(void) {
    uint8_t data = 0;
    
    // Імпульс защіпки (низький рівень завантажує дані)
    LATCH_PORT->BSRR = LATCH_PIN << 16;
    __NOP();
    LATCH_PORT->BSRR = LATCH_PIN;
    
    // Зчитування 8 біт
    for (int i = 0; i < 8; i++) {
        data <<= 1;
        if (DATA_PORT->IDR & DATA_PIN) {
            data |= 1;
        }
        
        // Тактовий імпульс
        CLOCK_PORT->BSRR = CLOCK_PIN;
        __NOP();
        CLOCK_PORT->BSRR = CLOCK_PIN << 16;
    }
    
    return data;
}
