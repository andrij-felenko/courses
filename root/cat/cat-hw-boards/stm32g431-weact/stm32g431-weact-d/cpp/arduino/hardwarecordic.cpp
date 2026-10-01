#include <stm32g4xx_ll_cordic.h>
#include <stm32g4xx_ll_bus.h>

class HardwareCordic {
public:
    static void init() {
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_CORDIC);
        LL_CORDIC_Config(CORDIC, LL_CORDIC_FUNCTION_COSINE, 
                         LL_CORDIC_PRECISION_6CYCLES, 
                         LL_CORDIC_SCALE_0, 
                         LL_CORDIC_NBWRITE_1, 
                         LL_CORDIC_NBREAD_2, 
                         LL_CORDIC_INSIZE_32BITS, 
                         LL_CORDIC_OUTSIZE_32BITS);
    }

    static void computeSinCos(int32_t inputQ31, int32_t &sinVal, int32_t &cosVal) {
        LL_CORDIC_WriteData(CORDIC, inputQ31);
        cosVal = LL_CORDIC_ReadData(CORDIC);
        sinVal = LL_CORDIC_ReadData(CORDIC);
    }
};
