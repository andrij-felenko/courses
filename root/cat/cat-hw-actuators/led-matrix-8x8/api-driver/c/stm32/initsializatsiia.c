int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();         // без такту на порт ніжки мертві
    __HAL_RCC_GPIOB_CLK_ENABLE();

    GPIO_InitTypeDef g = {0};
    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    for (int i = 0; i < 8; i++) {
        g.Pin = COL_PIN[i].pin;  HAL_GPIO_Init(COL_PIN[i].port, &g);
        g.Pin = ROW_PIN[i].pin;  HAL_GPIO_Init(ROW_PIN[i].port, &g);
        // стовпець «високий» → цятка темна; ключ закритий → рядок не живиться
        HAL_GPIO_WritePin(COL_PIN[i].port, COL_PIN[i].pin, GPIO_PIN_SET);
        HAL_GPIO_WritePin(ROW_PIN[i].port, ROW_PIN[i].pin, GPIO_PIN_RESET);
    }
    drawSmiley();        // покладемо в буфер щось видиме
    setupScanTimer();    // запускаємо розгортку в перериванні
    while (1) { }        // головний цикл вільний
}
