/* i2c.h — мінімальний I2C1 для датчика на комутованій шині.
 *
 * Тут важлива не швидкість, а два стани, через які плата не засинає:
 * заблокована рабом лінія SDA (підтяжки палять струм усю паузу) і периферійний
 * блок, залишений увімкненим після обміну.
 */
#ifndef I2C_H
#define I2C_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    I2C_OK = 0,
    I2C_ERR_TIMEOUT,
    I2C_ERR_NACK,
    I2C_ERR_BUS,        /* BERR / ARLO */
    I2C_ERR_STUCK       /* SDA притиснута до землі й після відновлення */
} i2c_err_t;

/* Вмикається лише коли шина 3V3_SW під напругою: підтяжки живляться з неї. */
i2c_err_t i2c1_init(void);
/* Вимикає блок і знімає тактування — інакше він живий і в сні. */
void i2c1_deinit(void);

i2c_err_t i2c1_read_reg(uint8_t addr7, uint8_t reg, uint8_t *buf, uint8_t len);

bool i2c1_bus_stuck(void);
i2c_err_t i2c1_bus_recover(void);

#endif /* I2C_H */
