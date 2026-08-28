volatile uint8_t curRow = 0;   // який рядок показуємо цієї ітерації

void scanStep(void) {
    // 1. ПОГАСИТИ попередній рядок ПЕРШИМ ділом — інакше буде перекриття.
    HAL_GPIO_WritePin(ROW_PIN[curRow].port, ROW_PIN[curRow].pin, GPIO_PIN_RESET);

    // 2. Перейти до наступного рядка по колу.
    curRow = (curRow + 1) & 7;               // 0,1,…,7,0,1,… (& 7 = % 8)

    // 3. Виставити на стовпці узор саме цього рядка.
    uint8_t bits = frame[curRow];
    for (uint8_t c = 0; c < 8; c++) {
        // спільний анод: цятка горить, коли стовпець притягнуто до нуля.
        GPIO_PinState lit = (bits & (1 << c)) ? GPIO_PIN_RESET : GPIO_PIN_SET;
        HAL_GPIO_WritePin(COL_PIN[c].port, COL_PIN[c].pin, lit);
    }

    // 4. І аж ТЕПЕР увімкнути новий рядок.
    HAL_GPIO_WritePin(ROW_PIN[curRow].port, ROW_PIN[curRow].pin, GPIO_PIN_SET);
}
