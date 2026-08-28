#include <stdint.h>
#include <stdbool.h>

/* Адреси заводських калібрувальних значень (STM32L4 / STM32G4) */
#define VREFINT_CAL_ADDR   ((uint16_t*)((uint32_t)0x1FFF75AA))
#define VREFINT_CAL_VOLT   3000U  /* 3.0 В, за яких завод калібрував VREF */

typedef enum {
    DVT_MODE_SLEEP_DEEP  = 0,
    DVT_MODE_CLOCK_MCO   = 1,
    DVT_MODE_ADC_VERIFY  = 2,
    DVT_MODE_BUS_STRESS  = 3
} dvt_test_mode_t;

typedef struct {
    uint32_t raw_vref_adc;
    uint32_t calculated_vdda_mv;
    int32_t  error_vs_nominal_mv;
} dvt_adc_metric_t;

/* Обчислення напруги живлення VDDA за калібруванням заводу */
dvt_adc_metric_t dvt_measure_vdda_accuracy(uint16_t adc_raw_vref) {
    dvt_adc_metric_t res;
    res.raw_vref_adc = adc_raw_vref;
    
    /* VDDA = VREFINT_CAL_VOLT * (*VREFINT_CAL_ADDR) / ADC_RAW */
    uint32_t vref_cal = *VREFINT_CAL_ADDR;
    if (adc_raw_vref == 0) {
        res.calculated_vdda_mv = 0;
        res.error_vs_nominal_mv = -3300;
        return res;
    }
    
    res.calculated_vdda_mv = (VREFINT_CAL_VOLT * vref_cal) / adc_raw_vref;
    res.error_vs_nominal_mv = (int32_t)res.calculated_vdda_mv - 3300;
    return res;
}

/* Налаштування виводу MCO (Microcontroller Clock Output) на вивід PA8 */
void dvt_configure_mco_output(bool enable, uint8_t prescaler_div) {
    /* Симуляція регістрової конфігурації тактового виводу */
    (void)enable;
    (void)prescaler_div;
}
