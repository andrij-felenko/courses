/* ============================================================================
   krok-3-isolated-uart.c — STM32 HAL: безпечна відправка UART через ізолятор
   ========================================================================== */

#include "main.h"

extern UART_HandleTypeDef huart2;
extern uint8_t B0505S_Is_Power_Healthy(void);

HAL_StatusTypeDef B0505S_Transmit_Isolated(uint8_t *pData, uint16_t Size, uint32_t Timeout) {
    // Блокування передачі, якщо ізольований домен не підтвердив свою роботу
    if (!B0505S_Is_Power_Healthy()) {
        return HAL_ERROR;
    }

    return HAL_UART_Transmit(&huart2, pData, Size, Timeout);
}
