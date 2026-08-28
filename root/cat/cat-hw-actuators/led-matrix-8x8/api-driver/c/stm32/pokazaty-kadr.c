int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitTypeDef g = {0};
    g.Pin   = DIN_PIN | CLK_PIN | LOAD_PIN;
    g.Mode  = GPIO_MODE_OUTPUT_PP;
    g.Pull  = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &g);

    max7219init();
    drawSmiley();
    max7219show();     // надіслали кадр — і він стоїть сам, чип його розгортає

    while (1) {
        // Нічого крутити не треба: MAX7219 сам тримає й розгортає картинку.
        // Щоб змінити зображення — перепиши frame[] і виклич max7219show() ще раз.
    }
}
