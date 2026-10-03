/* Автокалібрування та запуск OPAMP у режимі PGA через HAL API */
#include "stm32g4xx_hal.h"

void OPAMP_Init_PGA_HAL(OPAMP_HandleTypeDef *hopamp)
{
    hopamp->Instance = OPAMP1;
    hopamp->Init.PowerSupplyRange = OPAMP_POWERSUPPLY_HIGH;
    hopamp->Init.Mode             = OPAMP_PGA_MODE;
    hopamp->Init.NonInvertingInput= OPAMP_NONINVERTINGINPUT_IO0;
    hopamp->Init.InvertingInput   = OPAMP_INVERTINGINPUT_CONNECT_NO; /* Внутрішнє коло PGA */
    hopamp->Init.PgaGain          = OPAMP_PGA_GAIN_16_OR_MIN_GAIN;   /* Підсилення ×16 */
    hopamp->Init.UserTrimming     = OPAMP_TRIMMING_FACTORY;
    
    /* Крок 1: Запуск автокалібрування зсуву */
    HAL_OPAMP_SelfCalibrate(hopamp);
    
    /* Крок 2: Ініціалізація та запуск підсилювача */
    HAL_OPAMP_Init(hopamp);
    HAL_OPAMP_Start(hopamp);
}
