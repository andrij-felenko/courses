/* S1 — GPIO_Input із підтяжкою вгору (GPIO_PULLUP),
   LED1 — GPIO_Output push-pull; обидва задано в CubeMX */

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, GPIO_PIN_SET);   // SET = згашено

    while (1) {
        // у спокої на кнопці SET, натиснута садить вивід на землю — RESET
        if (HAL_GPIO_ReadPin(S1_GPIO_Port, S1_Pin) == GPIO_PIN_RESET)
            HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, GPIO_PIN_RESET); // світиться
        else
            HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, GPIO_PIN_SET);   // гасне
        HAL_Delay(10);
    }
}
