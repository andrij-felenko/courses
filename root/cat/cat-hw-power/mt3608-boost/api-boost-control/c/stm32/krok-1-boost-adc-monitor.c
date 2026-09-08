/* ============================================================================
   krok-1-boost-adc-monitor.c — STM32 HAL: моніторинг вихідної напруги до 28 В
   ========================================================================== */

#include "main.h"

extern ADC_HandleTypeDef hadc1;

#define DIVIDER_RATIO        11.0f

uint32_t MT3608_Get_Voltage_mV(void) {
    uint32_t raw = 0;

    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
        raw = HAL_ADC_GetValue(&hadc1);
    }
    HAL_ADC_Stop(&hadc1);

    // Переведення 12-бітного значення в мілівольти при опорній 3300 мВ
    uint32_t pin_mv = (raw * 3300) / 4095;
    uint32_t vout_mv = (uint32_t)(pin_mv * DIVIDER_RATIO);

    return vout_mv;
}
