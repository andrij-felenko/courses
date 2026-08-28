static IrObstacle front;

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    IrObstacle_Begin(&front, GPIOA, GPIO_PIN_0, 8, true);  // OUT давача на PA0

    while (1) {
        IrObstacle_Update(&front);            // опитати давач (неблокуюче)
        if (IrObstacle_Obstacle(&front))
            printf("ПЕРЕШКОДА\r\n");          // printf перенаправлено на UART
        else
            printf("вільно\r\n");
        // тут може бути будь-яка інша робота — Update() не блокує
    }
}
