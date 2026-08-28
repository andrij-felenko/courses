/* CubeMX: TIM3_CH1 у режимі PWM Generation.
   PSC дає такт ≈256 кГц, ARR = 255 → період 256 тактів ≈ 1 кГц, шкала 0…255. */
extern TIM_HandleTypeDef htim3;

void led_pwm_start(void)
{
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);           // таймер веде ніжку сам
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 77);   // 77/256 ≈ 30%
}

void led_pwm_set(uint8_t duty)                          // 0…255
{
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty); // новий поріг — і все
}
