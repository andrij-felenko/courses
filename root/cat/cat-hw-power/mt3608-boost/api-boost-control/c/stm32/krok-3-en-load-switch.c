/* ============================================================================
   krok-3-en-load-switch.c — STM32 HAL: послідовне увімкнення підвищувача
   ========================================================================== */

#include "main.h"

#define MT3608_EN_PIN        GPIO_PIN_11
#define MT3608_EN_PORT       GPIOA

#define LOAD_GATE_PIN        GPIO_PIN_12
#define LOAD_GATE_PORT       GPIOA

void MT3608_Power_On_Sequence(void) {
    // 1. Запуск перетворювача (ШІМ 1.2 МГц)
    HAL_GPIO_WritePin(MT3608_EN_PORT, MT3608_EN_PIN, GPIO_PIN_SET);
    
    // 2. Пауза 15 мс для заряду вихідних керамічних конденсаторів
    HAL_Delay(15);
    
    // 3. Відкриття силового ключа P-MOSFET (RESET = LOW = ON)
    HAL_GPIO_WritePin(LOAD_GATE_PORT, LOAD_GATE_PIN, GPIO_PIN_RESET);
}

void MT3608_Power_Off(void) {
    // Відключаємо навантаження, потім гасимо генератор
    HAL_GPIO_WritePin(LOAD_GATE_PORT, LOAD_GATE_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(MT3608_EN_PORT, MT3608_EN_PIN, GPIO_PIN_RESET);
}
