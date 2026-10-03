// Системний обробник помилок обчислень на LL API
#include "stm32g4xx_ll_fmac.h"
#include "stm32g4xx_ll_cordic.h"

class ProcessingPipelineGuard {
public:
    static void check_and_recover() {
        if (LL_FMAC_IsActiveFlag_SAT(FMAC)) {
            LL_FMAC_ClearFlag_SAT(FMAC);
            LL_FMAC_Disable(FMAC);
            LL_FMAC_Enable(FMAC);
        }
        
        if (LL_CORDIC_IsActiveFlag_ERR(CORDIC)) {
            /* Скидання регістра стану CORDIC через макрос */
            CORDIC->SR = 0;
        }
    }
};
