/* i2c.h — апаратний TWI ATmega328P із таймаутом і відновленням шини.
 *
 * Ключова відмінність від навчальних драйверів: жоден цикл очікування тут
 * не безкінечний. Іскріння щіток мотора наводить перешкоду на SDA, ведений
 * залипає посеред байта — і безкінечний `while (!(TWCR & (1<<TWINT)))`
 * вішає весь контур керування намертво. */

#ifndef I2C_H
#define I2C_H

#include <stdint.h>

typedef enum {
    I2C_OK = 0,
    I2C_ERR_TIMEOUT,   /* Апарат не підняв TWINT за відведений час */
    I2C_ERR_NACK,      /* Ведений не відповів на адресу або байт */
    I2C_ERR_BUS        /* Стан TWI не той, якого чекали */
} i2c_status_t;

/* Скільки чекати одну подію TWI, мікросекунди. Один байт на 400 кГц
 * триває ~22 мкс, тож 2000 мкс — це вже безумовна поламка. */
#define I2C_TIMEOUT_US 2000u

void i2c_init(void);

i2c_status_t i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value);
i2c_status_t i2c_read_regs(uint8_t dev_addr, uint8_t reg, uint8_t *dst, uint8_t len);

/* Ручне визволення шини: дев'ять імпульсів на SCL, щоб ведений домовив
 * свій байт і відпустив SDA, потім коректний STOP. Після цього TWI
 * ініціалізується наново. */
void i2c_bus_recover(void);

#endif /* I2C_H */
