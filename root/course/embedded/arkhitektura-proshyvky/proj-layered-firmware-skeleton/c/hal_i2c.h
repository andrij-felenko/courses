// hal/hal_i2c.h
#ifndef HAL_I2C_H
#define HAL_I2C_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_I2C_OK = 0,
    HAL_I2C_ERR_NACK,
    HAL_I2C_ERR_TIMEOUT,
    HAL_I2C_ERR_BUS
} hal_i2c_status_t;

// Таблиця операцій віртуальної шини I2C
typedef struct hal_i2c_bus_ops {
    hal_i2c_status_t (*write_reg)(void* context, uint8_t dev_addr, uint8_t reg_addr, 
                                  const uint8_t* data, size_t len);
    hal_i2c_status_t (*read_reg)(void* context, uint8_t dev_addr, uint8_t reg_addr, 
                                 uint8_t* data, size_t len);
} hal_i2c_bus_ops_t;

typedef struct hal_i2c_bus {
    const hal_i2c_bus_ops_t* ops;
    void* context; // Апаратний дескриптор (I2C_TypeDef* або Mock-буфер)
} hal_i2c_bus_t;

#endif // HAL_I2C_H
