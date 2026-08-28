/* Вивід під базу налаштовано в CubeMX як GPIO_Output (push-pull),
   такт порту вже піднято в MX_GPIO_Init(). */
#define MOTOR_PORT GPIOA
#define MOTOR_PIN  GPIO_PIN_5      // GPIO → Rb → база NPN-ключа

/* старт: транзистор закритий, мотор стоїть */
HAL_GPIO_WritePin(MOTOR_PORT, MOTOR_PIN, GPIO_PIN_RESET);

while (1) {                        /* нескінченний цикл main() */
    HAL_GPIO_WritePin(MOTOR_PORT, MOTOR_PIN, GPIO_PIN_SET);   // база відкрита → мотор крутиться
    HAL_Delay(2000);
    HAL_GPIO_WritePin(MOTOR_PORT, MOTOR_PIN, GPIO_PIN_RESET); // база закрита → мотор стоїть
    HAL_Delay(2000);
}
