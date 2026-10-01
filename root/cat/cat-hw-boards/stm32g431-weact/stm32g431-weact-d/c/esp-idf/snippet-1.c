#include "stm32g4xx_hal.h"

CORDIC_HandleTypeDef hcordic;

// Ініціалізація модуля CORDIC
void Init_CORDIC(void) {
    hcordic.Instance = CORDIC;
    HAL_CORDIC_Init(&hcordic);
}

// Апаратне обчислення sin(theta) та cos(theta)
void Calculate_SinCos(int32_t angle_q31, int32_t *sin_out, int32_t *cos_out) {
    CORDIC_ConfigTypeDef config;
    config.Function = CORDIC_FUNCTION_COSINE; // Режим розрахунку Cosine/Sine
    config.Precision = CORDIC_PRECISION_6CYCLES;
    config.Scale = CORDIC_SCALE_0;
    config.NBWRITE = CORDIC_NBWRITE_1;
    config.NBREAD = CORDIC_NBREAD_2;
    config.InSize = CORDIC_INSIZE_32BITS;
    config.OutSize = CORDIC_OUTSIZE_32BITS;
    
    HAL_CORDIC_Configure(&hcordic, &config);
    HAL_CORDIC_Calculate(&hcordic, &angle_q31, sin_out, 1, 10);
}
