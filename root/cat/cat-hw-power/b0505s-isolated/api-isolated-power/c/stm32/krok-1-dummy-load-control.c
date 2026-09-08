/* ============================================================================
   krok-1-dummy-load-control.c — STM32 HAL: комутація баласту B0505S
   ========================================================================== */

#include "main.h"

#define DUMMY_LOAD_PIN       GPIO_PIN_8
#define DUMMY_LOAD_PORT      GPIOB

#define ISO_PWR_EN_PIN       GPIO_PIN_9
#define ISO_PWR_EN_PORT      GPIOB

void B0505S_Init_Sequence(void) {
    // 1. Спочатку підключаємо баласт (SET = Active HIGH)
    HAL_GPIO_WritePin(DUMMY_LOAD_PORT, DUMMY_LOAD_PIN, GPIO_PIN_SET);
    
    // 2. Подаємо первинне живлення на B0505S
    HAL_GPIO_WritePin(ISO_PWR_EN_PORT, ISO_PWR_EN_PIN, GPIO_PIN_SET);
    
    // Пауза 20 мс для заряду вихідних конденсаторів B0505S (10 мкФ)
    HAL_Delay(20);
}

void B0505S_Set_Peripheral_Active(uint8_t is_active) {
    if (is_active) {
        // Вимикаємо баластний резистор, коли трансивер активний
        HAL_GPIO_WritePin(DUMMY_LOAD_PORT, DUMMY_LOAD_PIN, GPIO_PIN_RESET);
    } else {
        // Вмикаємо баласт перед переведенням лінії в режим очікування
        HAL_GPIO_WritePin(DUMMY_LOAD_PORT, DUMMY_LOAD_PIN, GPIO_PIN_SET);
    }
}
