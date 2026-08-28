    // Пін IRQ у CubeMX: GPIO_MODE_IT_RISING, Pull-down, лінія EXTI0 увімкнена.
    // Тут лишається тільки дозволити переривання цієї лінії:
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

// Обробник переривання: КОРОТКО — лише прапорець.
// HAL кличе цей callback з EXTI0_IRQHandler для всіх ліній — звіряємо пін.
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == IRQ_PIN) irqTriggered = true;
}
