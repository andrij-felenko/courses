#define MIN_LEVEL 480         /* мінімум середнього ІЧ у 12-бітних одиницях */

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init(); MX_DMA_Init(); MX_ADC1_Init(); MX_TIM3_Init();

    flick.win_start = HAL_GetTick();
    HAL_ADC_Start_DMA(&hadc1, (uint32_t *)&adc_raw, 1);  /* вибірку жене TIM3 */
    HAL_TIM_Base_Start(&htim3);                          /* 200 Гц, без жодного delay */

    uint32_t t = 0;
    while (1) {
        /* Головний цикл лише друкує: рахунок уже зробив callback у перериванні. */
        if (HAL_GetTick() - t > 200) {
            t = HAL_GetTick();
            bool bright   = flicker_level() > MIN_LEVEL;   /* є помітний ІЧ */
            bool flickers = flicker_flame();               /* і він пульсує 2..20 Гц */
            printf("рівень=%d  f=%.1f Гц  →  %s\r\n",
                   flicker_level(), flick.last_freq,
                   (bright && flickers) ? "ВОГОНЬ" : "спокій");
        }
    }
}
