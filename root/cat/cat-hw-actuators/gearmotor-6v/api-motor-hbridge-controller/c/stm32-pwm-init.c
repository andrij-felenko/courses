// Ініціалізація таймера STM32 HAL для генерації ультразвукового ШІМ 20 кГц
// Тактова частота шини APB1/APB2 таймера TIM1 дорівнює 84 МГц
TIM_HandleTypeDef htim1;

void stm32_pwm_init(void)
{
    TIM_OC_InitTypeDef sConfigOC = {0};

    htim1.Instance = TIM1;
    htim1.Init.Prescaler = 0; // Робота на повній тактовій частоті 84 МГц
    htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
    // ARR = (84 000 000 / 20 000) - 1 = 4199 відліків
    htim1.Init.Period = 4199;
    htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim1.Init.RepetitionCounter = 0;
    HAL_TIM_PWM_Init(&htim1);

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 0; // Початковий коефіцієнт заповнення 0%
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    
    HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1);
    HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_2);

    // Запуск каналів ШІМ із безпечним нульовим рівнем
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
}
