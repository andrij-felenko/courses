// ніжку зумера заведено на вихід TIM3_CH1; таймер налаштовано в режимі PWM
extern TIM_HandleTypeDef htim3;

void buzzer_tone(uint32_t freq_hz)
{
    // період лічильника задає частоту: f = f_тайм / ((PSC+1)·(ARR+1))
    uint32_t tim_clk = HAL_RCC_GetPCLK1Freq() * 2U;
    uint32_t arr = tim_clk / ((htim3.Init.Prescaler + 1U) * freq_hz) - 1U;

    __HAL_TIM_SET_AUTORELOAD(&htim3, arr);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, arr / 2U);  // 50 % — меандр
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    // процесор тут уже вільний — ніжку смикає таймер
}
