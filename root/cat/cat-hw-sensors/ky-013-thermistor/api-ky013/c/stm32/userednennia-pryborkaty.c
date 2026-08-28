// у HAL мікросекундної затримки нема: беремо лічильник тактів DWT
// (його вмикають один раз на старті: CoreDebug->DEMCR |= TRCENA; DWT->CTRL |= 1)
static void delay_us(uint32_t us) {
    uint32_t t0 = DWT->CYCCNT;
    uint32_t n  = us * (SystemCoreClock / 1000000U);
    while (DWT->CYCCNT - t0 < n) { }
}

// середній сирий відлік із N вимірів (шум давиться як √N)
static uint16_t read_raw_averaged(uint8_t samples) {
    uint32_t acc = 0;                       // 32 біти: 64×4095 не переповнить
    for (uint8_t i = 0; i < samples; i++) {
        acc += adc_read();
        delay_us(200);                      // дати входу АЦП «устоятися»
    }
    return (uint16_t)(acc / samples);
}
