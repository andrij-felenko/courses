#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

// Граничні пороги напруги елемента CR2032 (у мілівольтах)
#define VBAT_MV_GOOD         2800U   // Батарея повністю заряджена (> 2.8 В)
#define VBAT_MV_WARNING      2400U   // Попередження про знос (2.4..2.8 В)
#define VBAT_MV_CRITICAL     2100U   // Критичний розряд (< 2.4 В, необхідна заміна)
#define VBAT_DIVIDER_COEFF   4U      // Внутрішній апаратний подільник STM32F4 (1/4)

typedef enum {
    BATTERY_STATUS_OK = 0,
    BATTERY_STATUS_LOW,
    BATTERY_STATUS_CRITICAL,
    BATTERY_STATUS_ERROR
} battery_status_t;

typedef struct {
    uint32_t voltage_mv;
    battery_status_t status;
} vbat_report_t;

extern ADC_HandleTypeDef hadc1;

/**
 * @brief  Виконати безпечне вимірювання напруги на виводі VBAT.
 * @note   Аналоговий міст вмикається лише на час перетворення АЦП.
 */
vbat_report_t vbat_measure_voltage(void)
{
    vbat_report_t report = { .voltage_mv = 0, .status = BATTERY_STATUS_ERROR };
    ADC_ChannelConfTypeDef sConfig = {0};

    // 1. Увімкнення тактування модуля керування живленням та АЦП
    __HAL_RCC_PWR_CLK_ENABLE();
    
    // 2. Активація внутрішнього аналогового моста дільника VBAT
    // Встановлення біта VBATE у регістрі ADC->CCR
    ADC->CCR |= ADC_CCR_VBATE;

    // 3. Конфігурація каналу АЦП для вимірювання VBAT (ADC1_IN18 для STM32F4)
    sConfig.Channel      = ADC_CHANNEL_VBAT;
    sConfig.Rank         = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES; // Максимальний час вибірки для високоомного дільника

    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
        ADC->CCR &= ~ADC_CCR_VBATE; // Вимикаємо міст при помилці
        return report;
    }

    // 4. Запуск перетворення
    if (HAL_ADC_Start(&hadc1) == HAL_OK) {
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            uint32_t raw_adc = HAL_ADC_GetValue(&hadc1);
            
            // Розрахунок напруги: V_vbat = (raw / 4095) * Vdda * 4
            // Використовуємо цілочисельну арифметику у мілівольтах (припускаємо Vdda = 3300 мВ)
            uint32_t vdda_mv = 3300U;
            report.voltage_mv = (raw_adc * vdda_mv * VBAT_DIVIDER_COEFF) / 4095U;

            // 5. Класифікація стану батареї
            if (report.voltage_mv >= VBAT_MV_GOOD) {
                report.status = BATTERY_STATUS_OK;
            } else if (report.voltage_mv >= VBAT_MV_WARNING) {
                report.status = BATTERY_STATUS_LOW;
            } else {
                report.status = BATTERY_STATUS_CRITICAL;
            }
        }
        HAL_ADC_Stop(&hadc1);
    }

    // 6. ОБОВ'ЯЗКОВО: Вимикаємо вимірювальний міст для зупинки витоку струму!
    ADC->CCR &= ~ADC_CCR_VBATE;

    return report;
}
