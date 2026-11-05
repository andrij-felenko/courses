#include "stm32f4xx_hal.h"
#include "cmsis_os2.h"
#include <stdint.h>

#define ADC_BUF_LEN           16
#define EWMA_SHIFT            3
#define THRESHOLD_WARN_RAW    3846  /* Відповідає ~3.1 В при 12-бітному АЦП та V_ref = 3.3 В */
#define THRESHOLD_CRIT_RAW    3598  /* Відповідає ~2.9 В */

#define FLAG_POWER_WARNING    (1U << 0)
#define FLAG_POWER_CRITICAL   (1U << 1)

typedef struct {
    uint16_t adc_raw_buffer[ADC_BUF_LEN];
    uint32_t filtered_voltage;
    uint8_t  current_state;
} PowerMonitor_t;

static PowerMonitor_t g_power_monitor;
extern osEventFlagsId_t g_power_event_flags;

void PowerMonitor_Init(ADC_HandleTypeDef *hadc) {
    g_power_monitor.filtered_voltage = 0;
    g_power_monitor.current_state = 0;
    HAL_ADC_Start_DMA(hadc, (uint32_t *)g_power_monitor.adc_raw_buffer, ADC_BUF_LEN);
}

void PowerMonitor_ProcessFromISR(void) {
    uint32_t sum = 0;
    for (size_t i = 0; i < ADC_BUF_LEN; ++i) {
        sum += g_power_monitor.adc_raw_buffer[i];
    }
    uint32_t average_sample = sum / ADC_BUF_LEN;

    if (g_power_monitor.filtered_voltage == 0) {
        g_power_monitor.filtered_voltage = average_sample;
    } else {
        g_power_monitor.filtered_voltage = ((g_power_monitor.filtered_voltage << EWMA_SHIFT) 
                                            - g_power_monitor.filtered_voltage 
                                            + average_sample) >> EWMA_SHIFT;
    }

    if (g_power_monitor.filtered_voltage < THRESHOLD_CRIT_RAW) {
        g_power_monitor.current_state = 2;
        osEventFlagsSet(g_power_event_flags, FLAG_POWER_CRITICAL);
    } else if (g_power_monitor.filtered_voltage < THRESHOLD_WARN_RAW) {
        g_power_monitor.current_state = 1;
        osEventFlagsSet(g_power_event_flags, FLAG_POWER_WARNING);
    } else {
        g_power_monitor.current_state = 0;
    }
}

void vPowerTask(void *argument) {
    (void)argument;
    for (;;) {
        uint32_t flags = osEventFlagsWait(g_power_event_flags, 
                                          FLAG_POWER_WARNING | FLAG_POWER_CRITICAL, 
                                          osFlagsWaitAny, 
                                          osWaitForever);
        if (flags & FLAG_POWER_CRITICAL) {
            /* Негайне збереження контексту у Backup RAM та зупинка запису у Flash */
            HAL_PWR_EnableBkUpAccess();
            HAL_ADC_Stop_DMA((ADC_HandleTypeDef *)argument);
        } else if (flags & FLAG_POWER_WARNING) {
            /* Зниження тактової частоти ядра та вимкнення периферії */
            SystemCoreClockUpdate();
        }
    }
}
