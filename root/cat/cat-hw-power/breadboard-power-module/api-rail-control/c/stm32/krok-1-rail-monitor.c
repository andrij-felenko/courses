/* ============================================================================
   krok-1-rail-monitor.c — STM32 HAL: точний вимір напруги шини через VREFINT
   ========================================================================== */

#include "main.h"

extern ADC_HandleTypeDef hadc1;

#define DIVIDER_RATIO        3.0f

// Адреса заводського калібрувального значення VREFINT у пам'яті (для STM32F4/G4)
#define VREFINT_CAL_ADDR     ((uint16_t*)((uint32_t)0x1FFF7A2A))
#define VREFINT_CAL_VOLTAGE  3300 // мВ

/**
 * Зчитує шину MB102 з корекцією на фактичну опорну напругу чіпа
 */
uint32_t STM32_Read_Rail_mV(void) {
    uint32_t raw_rail = 0;
    uint32_t raw_vref = 0;

    // 1. Читання каналу шини (наприклад, ADC_CHANNEL_1)
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = ADC_CHANNEL_1;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
        raw_rail = HAL_ADC_GetValue(&hadc1);
    }
    HAL_ADC_Stop(&hadc1);

    // 2. Читання внутрішнього VREFINT
    sConfig.Channel = ADC_CHANNEL_VREFINT;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
        raw_vref = HAL_ADC_GetValue(&hadc1);
    }
    HAL_ADC_Stop(&hadc1);

    if (raw_vref == 0) return 0;

    // Розрахунок реальної VDDA (опорної напруги чіпа):
    // VDDA = 3300 * (*VREFINT_CAL_ADDR) / raw_vref
    uint32_t vdda_mv = (uint32_t)VREFINT_CAL_VOLTAGE * (*VREFINT_CAL_ADDR) / raw_vref;

    // Розрахунок напруги на виводі та напруги шини
    uint32_t v_pin_mv = (raw_rail * vdda_mv) / 4095;
    uint32_t rail_mv = (uint32_t)(v_pin_mv * DIVIDER_RATIO);

    return rail_mv;
}
