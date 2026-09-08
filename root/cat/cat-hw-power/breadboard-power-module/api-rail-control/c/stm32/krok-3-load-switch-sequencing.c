/* ============================================================================
   krok-3-load-switch-sequencing.c — STM32 HAL: поетапна подача живлення
   ========================================================================== */

#include "main.h"

void MB102_Power_Sequence_Start(void) {
    // 1. Початковий стан: всі навантаження відключені
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET); // Пін сенсорів (OFF)
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET); // Пін радіо/моторів (OFF)

    // Пауза для заряджання буферних ємностей MB102 (100 мкФ)
    HAL_Delay(150);

    // Етап 1: Підключення слабкострумових сенсорів
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET); // ON
    HAL_Delay(80);

    // Етап 2: Підключення силової частини
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET); // ON
    HAL_Delay(50);
}
