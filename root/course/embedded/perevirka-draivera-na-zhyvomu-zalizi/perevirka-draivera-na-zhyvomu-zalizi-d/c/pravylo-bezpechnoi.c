/* Коректне переведення шини SPI в енергозберігаючий режим на C (STM32 HAL) */
void sensor_enter_low_power_gpio_c(void) {
    GPIO_InitTypeDef gpio_init = {0};
    
    /* Деініціалізація апаратного блоку SPI */
    HAL_SPI_DeInit(&hspi1);
    
    /* Переведення сигнальних ліній у режим Analog Input для усунення витоків */
    gpio_init.Pin = GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7; /* SCK, MISO, MOSI */
    gpio_init.Mode = GPIO_MODE_ANALOG;
    gpio_init.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &gpio_init);
    
    /* Лінію CS притягуємо до 0 або також переводимо в Analog */
    gpio_init.Pin = GPIO_PIN_4;
    HAL_GPIO_Init(GPIOA, &gpio_init);
}
