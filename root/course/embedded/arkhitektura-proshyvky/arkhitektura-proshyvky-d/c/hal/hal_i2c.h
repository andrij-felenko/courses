/* hal/hal_i2c.h — сторона того, ХТО КОРИСТУЄТЬСЯ шиною.
 * Драйвери BSP бачать лише ці функції: «прочитай N регістрів мікросхеми»,
 * «запиши байт у регістр». Ані регістрів контролера I2C, ані вендорних
 * дескрипторів тут немає й бути не може. */
#ifndef HAL_I2C_H
#define HAL_I2C_H

#include "hal/hal_i2c_ops.h"

/* Чи придатна шина до вжитку: є таблиця операцій і обидві обов'язкові функції. */
bool hal_i2c_bus_is_valid(const hal_i2c_bus_t *bus);

/* Прочитати len байтів, починаючи з регістра reg_addr. Використовує
 * write_read, якщо порт її надав, інакше складає з write + read. */
hal_i2c_status_t hal_i2c_read_regs(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                   uint8_t reg_addr, uint8_t *dst, size_t len);

hal_i2c_status_t hal_i2c_read_reg(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                  uint8_t reg_addr, uint8_t *value);

hal_i2c_status_t hal_i2c_write_reg(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                   uint8_t reg_addr, uint8_t value);

/* Записати байт у регістр і перечитати його. Дешева перевірка того, що
 * мікросхема справді прийняла конфігурацію, а не лише підтвердила адресу. */
hal_i2c_status_t hal_i2c_write_reg_verify(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                          uint8_t reg_addr, uint8_t value);

/* Чи відгукується мікросхема за адресою (запис нульової довжини). */
hal_i2c_status_t hal_i2c_probe(const hal_i2c_bus_t *bus, uint8_t dev_addr);

#endif /* HAL_I2C_H */
