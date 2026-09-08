/* ============================================================================
   krok-2-isolated-heartbeat.c — STM32 HAL: перевірка сигналу оптопари
   ========================================================================== */

#include "main.h"

static volatile uint32_t s_last_pulse_tick = 0;

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_10) { // Пін з'єднаний з колектором фототранзистора
        s_last_pulse_tick = HAL_GetTick();
    }
}

uint8_t B0505S_Is_Power_Healthy(void) {
    // Якщо від останнього імпульсу минуло більше 60 мс — живлення вторинки зникло
    if ((HAL_GetTick() - s_last_pulse_tick) > 60) {
        return 0; // Fault
    }
    return 1;     // Healthy
}
