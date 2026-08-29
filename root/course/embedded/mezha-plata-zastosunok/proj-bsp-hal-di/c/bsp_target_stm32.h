/* bsp_target_stm32.h — цільова реалізація контракту плати для STM32F4. */
#ifndef BSP_TARGET_STM32_H
#define BSP_TARGET_STM32_H

#include "bsp_interface.h"

/* Ставить лінії у безпечний стан і зчитує калібрування BME280.
 * Викликати ПІСЛЯ MX_GPIO_Init/MX_ADC1_Init/MX_I2C1_Init/MX_RTC_Init. */
bsp_status_t stm32_bsp_init(void);

/* Готова таблиця методів — саме її отримує супервізор у прошивці. */
extern const bsp_driver_t stm32_bsp_driver;

#endif /* BSP_TARGET_STM32_H */
