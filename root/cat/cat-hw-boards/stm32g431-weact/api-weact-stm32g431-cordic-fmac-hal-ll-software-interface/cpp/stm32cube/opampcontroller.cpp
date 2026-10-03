// Налаштування OPAMP1 через LL API
#include "stm32g4xx_ll_opamp.h"

class OpampController {
public:
    static void init_pga_ll() {
        /* Увімкнення підсилення ×16 та підключення виходу на внутрішній ADC */
        LL_OPAMP_SetMode(OPAMP1, LL_OPAMP_MODE_PGA);
        LL_OPAMP_SetPGAGain(OPAMP1, LL_OPAMP_PGA_GAIN_16);
        LL_OPAMP_SetInputNonInverting(OPAMP1, LL_OPAMP_INPUT_NONINVERT_IO0);
        
        /* Запуск калібрування n/p-транзисторів */
        LL_OPAMP_StartCalibration(OPAMP1, LL_OPAMP_TRIMMING_FACTORY);
        
        /* Увімкнення підсилювача */
        LL_OPAMP_Enable(OPAMP1);
    }
};
