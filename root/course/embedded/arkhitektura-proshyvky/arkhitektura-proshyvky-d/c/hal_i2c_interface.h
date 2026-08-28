// hal_i2c_interface.h — Інверсія залежностей для шини I2C у C
#ifndef HAL_I2C_INTERFACE_H
#define HAL_I2C_INTERFACE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    bool (*write)(void* user_ctx, uint8_t dev_addr, const uint8_t* data, size_t len);
    bool (*read)(void* user_ctx, uint8_t dev_addr, uint8_t* data, size_t len);
    bool (*write_read)(void* user_ctx, uint8_t dev_addr, const uint8_t* wdata, 
                       size_t wlen, uint8_t* rdata, size_t rlen);
} hal_i2c_ops_t;

typedef struct {
    const hal_i2c_ops_t* ops;
    void* user_ctx; // Вказівник на I2C_HandleTypeDef на STM32 або Mock-об'єкт у тестах
} hal_i2c_bus_t;

#endif // HAL_I2C_INTERFACE_H
