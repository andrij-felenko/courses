// Конфігуратор прискорювача FMAC із використанням LL API
#include "stm32g4xx_ll_fmac.h"

class FmacFirFilter {
public:
    static void configure_ll(uint8_t x1_base, uint8_t x1_size,
                             uint8_t x2_base, uint8_t x2_size,
                             uint8_t y_base,  uint8_t y_size,
                             uint8_t num_taps)
    {
        LL_FMAC_ConfigX1Buf(FMAC, x1_base, x1_size, 1); /* Поріг заповнення = 1 */
        LL_FMAC_ConfigX2Buf(FMAC, x2_base, x2_size);
        LL_FMAC_ConfigYBuf(FMAC, y_base, y_size, 1);
        
        LL_FMAC_Configure(FMAC, LL_FMAC_PARAM_FUNC_FIR, num_taps, 0, 0, LL_FMAC_PARAM_CLIP_DISABLE);
        LL_FMAC_Enable(FMAC);
    }
};
