extern ADC_HandleTypeDef hadc1;           // канал з AO налаштовано в CubeMX
#define WIN 50u                           // вікно вимірювання, мс

uint16_t measure_peak_to_peak(void) {
    uint32_t start = HAL_GetTick();
    uint16_t lo = 4095, hi = 0;           // межі для 12-бітного АЦП STM32
    while (HAL_GetTick() - start < WIN) {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            uint16_t v = HAL_ADC_GetValue(&hadc1);
            if (v < lo) lo = v;
            if (v > hi) hi = v;
        }
        HAL_ADC_Stop(&hadc1);
    }
    return hi - lo;                       // розмах у відліках АЦП
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init();
    MX_ADC1_Init(); MX_USART2_UART_Init();
    while (1) {
        uint16_t amp = measure_peak_to_peak();
        printf("розмах: %u\r\n", amp);    // мале — тихо, велике — гучно
        // поріг під 12-бітну шкалу — теж просто число
        if (amp > 250) printf("  → гучно!\r\n");
    }
}
