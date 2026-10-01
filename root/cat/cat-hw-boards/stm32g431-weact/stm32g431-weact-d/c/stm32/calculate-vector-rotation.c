#include "stm32g4xx_hal.h"

extern CORDIC_HandleTypeDef hcordic;

// Апаратне обчислення sin та cos для векторного перетворення
void calculate_vector_rotation(int32_t angle_q31, int32_t *sin_out, int32_t *cos_out) {
    CORDIC_ConfigTypeDef sConfig = {0};
    sConfig.Function = CORDIC_FUNCTION_COSINE;
    sConfig.Precision = CORDIC_PRECISION_6CYCLES;
    sConfig.Scale = CORDIC_SCALE_0;
    sConfig.NbWrite = CORDIC_NBWRITE_1;
    sConfig.NbRead = CORDIC_NBREAD_2;
    sConfig.InSize = CORDIC_INSIZE_32BITS;
    sConfig.OutSize = CORDIC_OUTSIZE_32BITS;
    
    HAL_CORDIC_Configure(&hcordic, &sConfig);
    
    int32_t out_buf[2];
    HAL_CORDIC_CalculateZO(&hcordic, &angle_q31, out_buf, 1, 100);
    *cos_out = out_buf[0];
    *sin_out = out_buf[1];
}
