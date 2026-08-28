// Те саме на STM32 HAL: частоту задають дільник (PSC) і період (ARR).
// 84 МГц / (PSC+1) / (ARR+1) = 5 кГц; беремо PSC = 65, ARR = 255 —
// тоді ARR заразом дає ту саму 8-бітну шкалу шпаруватості 0…255.
TIM_HandleTypeDef htim4;

void sw_begin_pwm(sw_t *s, uint32_t channel) {
    __HAL_RCC_TIM4_CLK_ENABLE();
    htim4.Instance           = TIM4;
    htim4.Init.Prescaler     = 65;                       // 84 МГц / 66 ≈ 1.27 МГц
    htim4.Init.CounterMode   = TIM_COUNTERMODE_UP;
    htim4.Init.Period        = 255;                      // 1.27 МГц / 256 ≈ 5 кГц
    htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_PWM_Init(&htim4);

    TIM_OC_InitTypeDef oc = {
        .OCMode     = TIM_OCMODE_PWM1,
        .Pulse      = s->active_low ? 255 : 0,           // старт: вимкнено
        .OCPolarity = TIM_OCPOLARITY_HIGH,
        .OCFastMode = TIM_OCFAST_DISABLE,
    };
    HAL_TIM_PWM_ConfigChannel(&htim4, &oc, channel);
    HAL_TIM_PWM_Start(&htim4, channel);   // вивід у режим AF задає HAL_TIM_PWM_MspInit()
}
