// Ті самі три ручки на STM32, лише називаються по-таймерному:
// роздільність = ARR, частота = f_TIM/((PSC+1)·(ARR+1)), канал ≠ пін.
TIM_HandleTypeDef htim3;

void rgb_init(void) {
  __HAL_RCC_TIM3_CLK_ENABLE();
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 65 - 1;              // 84 МГц / 65 ≈ 1.29 МГц
  htim3.Init.Period    = 256 - 1;             // ARR = 255 → duty 0..255 (8 біт)
  htim3.Init.CounterMode   = TIM_COUNTERMODE_UP;   // 1.29 МГц / 256 ≈ 5 кГц
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_PWM_Init(&htim3);

  TIM_OC_InitTypeDef oc = { .OCMode = TIM_OCMODE_PWM1, .Pulse = 0,
                            .OCPolarity = TIM_OCPOLARITY_HIGH, .OCFastMode = TIM_OCFAST_DISABLE };
  HAL_TIM_PWM_ConfigChannel(&htim3, &oc, TIM_CHANNEL_1);   // канал 1 → PB4 (AF2)
  HAL_TIM_PWM_ConfigChannel(&htim3, &oc, TIM_CHANNEL_2);   // канал 2 → PB5
  HAL_TIM_PWM_ConfigChannel(&htim3, &oc, TIM_CHANNEL_3);   // канал 3 → PB0
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);
}
// (піни в режимі альтернативної функції — окремо, у HAL_TIM_MspPostInit)
