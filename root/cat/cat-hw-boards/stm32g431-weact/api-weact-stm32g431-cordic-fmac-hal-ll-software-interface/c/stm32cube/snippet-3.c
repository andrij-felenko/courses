/* Налаштування КІХ-фільтра в FMAC через HAL API */
#include "stm32g4xx_hal.h"

void FMAC_FIR_Config_HAL(FMAC_HandleTypeDef *hfmac, int16_t *coeffs, uint16_t num_coeffs)
{
    FMAC_FilterConfigTypeDef config;
    
    config.CoeffBaseAddress  = 0;
    config.CoeffBufferSize   = num_coeffs;
    config.InputBaseAddress  = num_coeffs;
    config.InputBufferSize   = num_coeffs + 8; /* Запас під циклічне зсунення */
    config.OutputBaseAddress = num_coeffs * 2 + 8;
    config.OutputBufferSize  = 16;
    
    config.FilterTypeDef     = FMAC_FILTER_FIR_ALTERNATE;
    config.P                 = num_coeffs; /* Кількість коефіцієнтів b_k */
    config.Q                 = 0;          /* Не використовується для FIR */
    config.R                 = 0;          /* Масштабний зсув результату */
    config.Clip              = FMAC_CLIP_DISABLED;
    
    HAL_FMAC_FilterConfig(hfmac, &config);
    HAL_FMAC_FilterPreload(hfmac, coeffs, num_coeffs, NULL, 0);
    HAL_FMAC_FilterStart(hfmac, NULL, 0);
}
