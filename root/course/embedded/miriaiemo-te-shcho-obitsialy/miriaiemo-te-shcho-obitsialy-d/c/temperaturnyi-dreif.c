#include <stdint.h>

#define VREFINT_CAL_ADDR ((uint16_t*)((uint32_t)0x1FFF75AA))
#define VREFINT_CAL_MV   3000U

/* Обчислення напруги живлення VDDA у мілівольтах за виміряним кодом VREFINT */
uint32_t ADC_Calculate_VDDA(uint16_t raw_vref_code) {
    if (raw_vref_code == 0) return 0;
    
    uint32_t vref_cal = *VREFINT_CAL_ADDR;
    /* VDDA = 3000 mV * VREFINT_CAL / RAW_ADC_CODE */
    return (VREFINT_CAL_MV * vref_cal) / raw_vref_code;
}

/* Обчислення реальної напруги на аналоговому вході каналу */
uint32_t ADC_Calculate_Channel_Millivolts(uint16_t raw_channel_code, uint16_t raw_vref_code) {
    uint32_t vdda_mv = ADC_Calculate_VDDA(raw_vref_code);
    /* V_channel = VDDA * RAW_CHANNEL / 4095 */
    return (vdda_mv * (uint32_t)raw_channel_code) / 4095U;
}
