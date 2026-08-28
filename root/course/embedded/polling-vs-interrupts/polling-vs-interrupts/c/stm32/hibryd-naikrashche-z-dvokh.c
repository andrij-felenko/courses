/* ніжка вже налаштована як вхід: SENSOR_GPIO_Port / SENSOR_Pin */
volatile uint32_t turns = 0;

int main(void) {
    HAL_Init();
    MX_GPIO_Init();

    GPIO_PinState prev = GPIO_PIN_RESET;
    while (1) {
        GPIO_PinState now = HAL_GPIO_ReadPin(SENSOR_GPIO_Port, SENSOR_Pin);
        if (prev == GPIO_PIN_RESET && now == GPIO_PIN_SET)  // висхідний фронт?
            turns++;
        prev = now;
        HAL_Delay(5);   // ... решта роботи циклу: екран, мережа, обрахунки ...
    }
}
