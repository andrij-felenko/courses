#include <stdint.h>
#include <stdbool.h>

/* Коди помилок операції */
typedef enum {
    ADC_SUCCESS = 0,
    ADC_ERR_TIMEOUT,
    ADC_ERR_OVERVOLTAGE
} AdcStatus;

/* Повернення результату через покажчик та код статусу */
AdcStatus adc_read_voltage(uint32_t channel, uint16_t* out_mv) {
    if (channel > 15) {
        return ADC_ERR_TIMEOUT;
    }
    /* Імітація зчитування апаратного регістра */
    *out_mv = 3300;
    return ADC_SUCCESS;
}
