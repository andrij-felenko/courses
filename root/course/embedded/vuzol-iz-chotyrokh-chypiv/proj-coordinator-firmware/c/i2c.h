#ifndef I2C_H
#define I2C_H

/* I2C1 у ролі ведучого: жорсткі тайм-аути замість очікування «поки не буде»
 * і дев'ятитактне розблокування шини, коли ведений тримає SDA у нулі. */

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_OK = 0,
    I2C_ERR_TIMEOUT,  /* прапорець не з'явився за відведений час */
    I2C_ERR_NACK,     /* ведений не підтвердив адресу чи байт    */
    I2C_ERR_BUSY      /* шина зайнята й розблокування не помогло */
} i2c_status_t;

void i2c_init(void);

i2c_status_t i2c_write(uint8_t addr7, const uint8_t *data, uint8_t len);
i2c_status_t i2c_write_reg(uint8_t addr7, uint8_t reg, uint8_t value);
i2c_status_t i2c_read_regs(uint8_t addr7, uint8_t reg, uint8_t *dst, uint8_t len);

/* Дев'ять тактів на SCL + коректний STOP. true — шина відпущена. */
bool i2c_bus_recover(void);

uint32_t i2c_recovery_count(void);

#endif /* I2C_H */
