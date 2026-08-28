volatile bool fired = false;                     // спільний прапорець

// верхня половина: HAL сам скидає прапорець EXTI й кличе цей callback
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == EVENT_Pin) fired = true;          // лише відмітити — і вийти
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();          // ніжка: GPIO_MODE_IT_FALLING + GPIO_PULLUP
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);

    while (1) {                                  // нижня половина: тут можна все
        if (fired) {
            fired = false;                       // скинути ПЕРЕД роботою
            printf("подія!\r\n");                // друк через retarget на UART
        }
    }
}
