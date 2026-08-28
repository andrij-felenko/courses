#include "main.h"
// пін S модуля -> PA9, у CubeMX виставлено GPIO_Output (тактування порту дає MX_GPIO_Init)
#define LASER_PORT GPIOA
#define LASER_PIN  GPIO_PIN_9

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();

    // старт з вимкненим променем — гарна звичка
    HAL_GPIO_WritePin(LASER_PORT, LASER_PIN, GPIO_PIN_RESET);

    while (1) {
        HAL_GPIO_WritePin(LASER_PORT, LASER_PIN, GPIO_PIN_SET);    // промінь увімкнено
        HAL_Delay(1000);
        HAL_GPIO_WritePin(LASER_PORT, LASER_PIN, GPIO_PIN_RESET);  // промінь вимкнено
        HAL_Delay(1000);
    }
}
