#ifndef I2C_MASTER_H
#define I2C_MASTER_H

#include <stddef.h>
#include <stdint.h>

#include "mcu_regs.h"

typedef enum {
    I2C_OK = 0,
    I2C_ERR_TIMEOUT,
    I2C_ERR_NACK,     /* AF: ніхто не притягнув SDA на 9-му такті */
    I2C_ERR_ARLO,     /* втрата арбітражу — на шині є інший ведучий */
    I2C_ERR_BERR,     /* START/STOP у неприпустимий момент */
    I2C_ERR_BUSY,     /* шина не звільнилася: кандидат на bus recovery */
    I2C_ERR_ARG
} i2c_status_t;

void i2c1_master_init(uint32_t pclk1_hz, uint32_t scl_hz);

i2c_status_t i2c1_write(uint8_t addr7, const uint8_t *data, size_t len);
i2c_status_t i2c1_read(uint8_t addr7, uint8_t *data, size_t len);

/* Класичне читання регістра давача: запис адреси регістра, повторний START,
   читання відповіді без звільнення шини між фазами. */
i2c_status_t i2c1_write_read(uint8_t addr7, const uint8_t *cmd, size_t cmd_len,
                             uint8_t *data, size_t len);

#endif /* I2C_MASTER_H */
