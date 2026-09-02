#ifndef I2C1_H
#define I2C1_H

#include <stdint.h>

typedef enum {
    I2C_OK = 0,
    I2C_ERR_BUSY,      /* BUSY не знімається — саме той симптом заклиненої шини */
    I2C_ERR_TIMEOUT,   /* подія не настала: ведений мовчить або тримає такт */
    I2C_ERR_NACK,      /* чип на шині є, але адресу не підтвердив */
    I2C_ERR_BUS        /* BERR: контролер побачив START/STOP не на своєму місці */
} i2c_status_t;

/* Налаштовує модуль на задану швидкість. Виводи PB6/PB7 має вже перевести в
   Alternate Function Open-Drain процедура i2c1_bus_recover() — тут їх не чіпаємо. */
void i2c1_init(uint32_t bus_hz);

/* Читання одного регістра веденого чипа: запис номера регістра, повторний
   START, читання байта з NACK і STOP. */
i2c_status_t i2c1_read_register(uint8_t addr7, uint8_t reg, uint8_t *value);

#endif /* I2C1_H */
