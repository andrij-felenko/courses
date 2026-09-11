// Запис шпаруватості в регістри порівняння CCR таймера STM32
void platform_pwm_set_duty(void *port, uint16_t pin, uint32_t compare_value)
{
    // Залежно від прив'язаного виводу оновлюємо відповідний канал TIM1
    if (pin == GPIO_PIN_8) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, compare_value);
    } else if (pin == GPIO_PIN_9) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, compare_value);
    }
}

void platform_gpio_write(void *port, uint16_t pin, bool level)
{
    HAL_GPIO_WritePin((GPIO_TypeDef*)port, pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
}
