// Увімкнути лічильник тактів DWT раз під час старту
static inline void cyccnt_enable(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   // біт 24
    DWT->CYCCNT = 0;
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;             // біт 0
}

// Виміряти ділянку (повертає такти)
static inline uint32_t measure(void) {
    uint32_t t0 = DWT->CYCCNT;
    work_under_test();
    return DWT->CYCCNT - t0;     // беззнакова різниця стійка до переповнення
}
