// C++ обгортка для обчислення тригонометрії через CORDIC LL
#include "stm32g4xx_ll_cordic.h"
#include <utility>

class CordicTrig {
public:
    static void init() {
        LL_CORDIC_Config(CORDIC, LL_CORDIC_FUNCTION_COSINE,
                         LL_CORDIC_PRECISION_6CYCLES, LL_CORDIC_SCALE_0,
                         LL_CORDIC_NBWRITE_1, LL_CORDIC_NBREAD_2,
                         LL_CORDIC_INSIZE_32BITS, LL_CORDIC_OUTSIZE_32BITS);
    }

    static std::pair<int32_t, int32_t> compute_sin_cos(int32_t angle_q31) {
        LL_CORDIC_WriteData(CORDIC, static_cast<uint32_t>(angle_q31));
        int32_t cos_val = static_cast<int32_t>(LL_CORDIC_ReadData(CORDIC));
        int32_t sin_val = static_cast<int32_t>(LL_CORDIC_ReadData(CORDIC));
        return {sin_val, cos_val};
    }
};
