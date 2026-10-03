/* Обробка переривань та відновлення FMAC/CORDIC через HAL API */
#include "stm32g4xx_hal.h"

void FMAC_CORDIC_ErrorHandler(FMAC_HandleTypeDef *hfmac, CORDIC_HandleTypeDef *hcordic)
{
    /* Перевірка насичення або опустіння буферів FMAC */
    if (__HAL_FMAC_GET_FLAG(hfmac, FMAC_FLAG_SAT)) {
        __HAL_FMAC_CLEAR_FLAG(hfmac, FMAC_FLAG_SAT);
        /* Скидання та повторна ініціалізація циклічних буферів */
        HAL_FMAC_FilterStop(hfmac);
        HAL_FMAC_FilterStart(hfmac, NULL, 0);
    }
    
    /* Перевірка помилок аргументу CORDIC */
    if (__HAL_CORDIC_GET_FLAG(hcordic, CORDIC_FLAG_ERR)) {
        __HAL_CORDIC_CLEAR_FLAG(hcordic, CORDIC_FLAG_ERR);
        /* Скидання периферійного блоку CORDIC */
        HAL_CORDIC_Init(hcordic);
    }
}
