// Ініціалізація та точна затримка через лічильник DWT у C
void dwt_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void dwt_delay_us(uint32_t us) {
    uint32_t start_cycles = DWT->CYCCNT;
    uint32_t required_cycles = us * (SystemCoreClock / 1000000);
    while ((DWT->CYCCNT - start_cycles) < required_cycles) {
        // Очікування завершення апаратного відліку
    }
}
