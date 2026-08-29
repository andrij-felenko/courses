/* ports/stm32f4/stm32_port.h — внутрішній інтерфейс порту STM32F4.
 * Заголовок бачать лише файли самого порту: застосунок отримує плату
 * через include/board.h і про існування цього файла не здогадується. */
#ifndef STM32_PORT_H
#define STM32_PORT_H

#include "hal/hal_gpio.h"
#include "hal/hal_i2c_ops.h"
#include "include/telemetry_record.h"

/* Піднімає контролер I2C1 (PB6/PB7) і віддає готовий дескриптор шини. */
const hal_i2c_bus_t *stm32_i2c1_init(void);

/* Таблиця операцій GPIO та контекст порту A/B/C. */
const hal_gpio_ops_t *stm32_gpio_ops(void);
void                 *stm32_gpio_port_b(void);

/* Передавач телеметрії: USART2, 115200 бод, вивід PA2. */
void stm32_uart_init(void);
void stm32_uart_report_record(void *ctx, const telemetry_record_t *rec);

/* Налаштовує зовнішнє переривання від кнопки на PA0. */
void stm32_button_exti_init(void);

#endif /* STM32_PORT_H */
