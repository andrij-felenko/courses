#include "driver/gpio.h"
#include "driver/adc.h"
#include "esp_timer.h"

#define PUMP_PWM_GPIO       GPIO_NUM_18
#define CURRENT_ADC_CHANNEL ADC1_CHANNEL_6 // ADC1 channel for shunt voltage

#define CURRENT_DRY_RUN_RAW 300  // ADC raw threshold for dry run (~0.35A)
#define CURRENT_STALL_RAW   2500 // ADC raw threshold for stall (~2.5A)
#define STABLE_RUN_DELAY_MS 300  // Ignore startup inrush current

typedef enum {
    PUMP_OK = 0,
    PUMP_ERROR_DRY_RUN,
    PUMP_ERROR_OVERCURRENT
} pump_status_t;

pump_status_t check_pump_health(uint32_t run_duration_ms) {
    int raw_adc = adc1_get_raw(CURRENT_ADC_CHANNEL);
    
    // Ignore readings during initial inrush transient
    if (run_duration_ms < STABLE_RUN_DELAY_MS) {
        return PUMP_OK;
    }
    
    if (raw_adc < CURRENT_DRY_RUN_RAW) {
        return PUMP_ERROR_DRY_RUN;
    } else if (raw_adc > CURRENT_STALL_RAW) {
        return PUMP_ERROR_OVERCURRENT;
    }
    
    return PUMP_OK;
}
