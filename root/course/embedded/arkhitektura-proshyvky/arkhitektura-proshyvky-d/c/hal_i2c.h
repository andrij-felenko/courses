// hal/hal_i2c.h
#ifndef HAL_I2C_H
#define HAL_I2C_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_I2C_STATUS_OK = 0,
    HAL_I2C_STATUS_NACK,
    HAL_I2C_STATUS_BUS_ERROR,
    HAL_I2C_STATUS_TIMEOUT
} hal_i2c_status_t;

typedef struct {
    hal_i2c_status_t (*mem_read)(void* ctx, uint8_t dev_addr, uint8_t reg_addr, 
                                 uint8_t* p_data, size_t size);
    hal_i2c_status_t (*mem_write)(void* ctx, uint8_t dev_addr, uint8_t reg_addr, 
                                  const uint8_t* p_data, size_t size);
} hal_i2c_driver_t;

typedef struct {
    const hal_i2c_driver_t* driver;
    void* context;
} hal_i2c_bus_t;

#endif // HAL_I2C_H
