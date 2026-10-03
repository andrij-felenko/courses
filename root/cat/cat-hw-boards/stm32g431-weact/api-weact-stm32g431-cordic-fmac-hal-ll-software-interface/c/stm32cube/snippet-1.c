/* Приклад обчислення sin/cos через CORDIC HAL та LL */
#include "stm32g4xx_hal.h"
#include "stm32g4xx_ll_cordic.h"

/* Варіант 1: Використання HAL API */
void CORDIC_Calculate_HAL(CORDIC_HandleTypeDef *hcordic, int32_t angle_q31, int32_t *sin_out, int32_t *cos_out)
{
    CORDIC_ConfigTypeDef config;
    config.Function  = CORDIC_FUNCTION_COSINE; /* Обчислення косинуса й синуса дуплетом */
    config.Precision = CORDIC_PRECISION_6CYCLES; /* 24 ітерації (6 циклів по 4 такти) */
    config.Scale     = CORDIC_SCALE_0;
    config.NbWrite   = CORDIC_NBWRITE_1;
    config.NbRead    = CORDIC_NBREAD_2;
    config.InSize    = CORDIC_INSIZE_32BITS;
    config.OutSize   = CORDIC_OUTSIZE_32BITS;
    
    HAL_CORDIC_Configure(hcordic, &config);
    
    int32_t input_buf[1]  = { angle_q31 };
    int32_t output_buf[2]; /* [0] = cos, [1] = sin */
    
    HAL_CORDIC_Calculate(hcordic, input_buf, output_buf, 1, HAL_MAX_DELAY);
    *cos_out = output_buf[0];
    *sin_out = output_buf[1];
}

/* Варіант 2: Прямий низькорівневий запис через LL API */
void CORDIC_Calculate_LL(int32_t angle_q31, int32_t *sin_out, int32_t *cos_out)
{
    /* Налаштування регістра CSR: функція COSINE, 24 ітерації, Q1.31 */
    LL_CORDIC_Config(CORDIC, LL_CORDIC_FUNCTION_COSINE,
                     LL_CORDIC_PRECISION_6CYCLES, LL_CORDIC_SCALE_0,
                     LL_CORDIC_NBWRITE_1, LL_CORDIC_NBREAD_2,
                     LL_CORDIC_INSIZE_32BITS, LL_CORDIC_OUTSIZE_32BITS);
    
    /* Запис вхідного кута у регістр WDATA запускає обчислення */
    LL_CORDIC_WriteData(CORDIC, (uint32_t)angle_q31);
    
    /* Зчитування двох результатів з регістра RDATA */
    *cos_out = (int32_t)LL_CORDIC_ReadData(CORDIC);
    *sin_out = (int32_t)LL_CORDIC_ReadData(CORDIC);
}
