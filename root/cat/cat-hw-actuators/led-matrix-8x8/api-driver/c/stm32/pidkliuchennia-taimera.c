TIM_HandleTypeDef htim2;

void setupScanTimer(void) {
    __HAL_RCC_TIM2_CLK_ENABLE();
    htim2.Instance = TIM2;
    // Шина таймера 72 МГц; передільник 72 → лічильник цокає 1 000 000 Гц.
    // Для 1000 переривань/с рахуємо до 1 000 000 / 1000 = 1000 тактів.
    htim2.Init.Prescaler     = 72 - 1;
    htim2.Init.CounterMode   = TIM_COUNTERMODE_UP;
    htim2.Init.Period        = 1000 - 1;   // 0..999 — це рівно 1000 кроків
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_Base_Init(&htim2);

    HAL_NVIC_SetPriority(TIM2_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(TIM2_IRQn);
    HAL_TIM_Base_Start_IT(&htim2);         // пустити таймер із перериванням
}

// Вектор віддає керування HAL, а HAL — у наш зворотний виклик нижче.
void TIM2_IRQHandler(void) { HAL_TIM_IRQHandler(&htim2); }

// Це і є та функція, яку таймер смикає 1000 разів на секунду.
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) scanStep();
}
