// CubeMX: EN → PB0, керування живленням → PB1, обидва GPIO_Output.
// huart1 — порт до модуля.
void enter_at_mode(void) {
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);    // EN високо — ЩЕ ДО живлення
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);  // на мить знеструмити…
    HAL_Delay(100);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);    // …і подати знову
    HAL_Delay(500);                                        // дати модулю прокинутись

    // перевідкриваємо порт на командній швидкості
    HAL_UART_DeInit(&huart1);
    huart1.Init.BaudRate = 38400;           // КОМАНДНА швидкість HC-05, не 9600!
    if (HAL_UART_Init(&huart1) != HAL_OK) Error_Handler();
}
