// hal/hal_i2c.h — контракт шини I2C. Жодного слова про STM32, ESP32 чи конкретний давач.
#ifndef HAL_I2C_H
#define HAL_I2C_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_I2C_OK = 0,
    HAL_I2C_ERR_NACK,      // Пристрій не підтвердив адресу або байт
    HAL_I2C_ERR_TIMEOUT,   // Ліміт очікування прапорця вичерпано
    HAL_I2C_ERR_BUS,       // Арбітраж програно, лінію притиснуто, помилка кадру
    HAL_I2C_ERR_ARG        // Некоректні аргументи виклику
} hal_i2c_status_t;

// Таблиця операцій віртуальної шини I2C.
// Реалізації: регістрова для STM32, заглушка для хостових тестів, будь-яка інша.
typedef struct hal_i2c_bus_ops {
    hal_i2c_status_t (*write_reg)(void* context, uint8_t dev_addr, uint8_t reg_addr,
                                  const uint8_t* data, size_t len);
    hal_i2c_status_t (*read_reg)(void* context, uint8_t dev_addr, uint8_t reg_addr,
                                 uint8_t* data, size_t len);
} hal_i2c_bus_ops_t;

typedef struct hal_i2c_bus {
    const hal_i2c_bus_ops_t* ops;
    void* context;  // Апаратний дескриптор (I2C_TypeDef*) або буфер заглушки
} hal_i2c_bus_t;

// Тонкі обгортки: перевіряють контракт один раз, а не в кожному драйвері.
static inline hal_i2c_status_t hal_i2c_read_reg(const hal_i2c_bus_t* bus, uint8_t dev_addr,
                                                uint8_t reg_addr, uint8_t* data, size_t len)
{
    if (!bus || !bus->ops || !bus->ops->read_reg || (!data && len)) {
        return HAL_I2C_ERR_ARG;
    }
    return bus->ops->read_reg(bus->context, dev_addr, reg_addr, data, len);
}

static inline hal_i2c_status_t hal_i2c_write_reg(const hal_i2c_bus_t* bus, uint8_t dev_addr,
                                                 uint8_t reg_addr, const uint8_t* data, size_t len)
{
    if (!bus || !bus->ops || !bus->ops->write_reg || (!data && len)) {
        return HAL_I2C_ERR_ARG;
    }
    return bus->ops->write_reg(bus->context, dev_addr, reg_addr, data, len);
}

static inline hal_i2c_status_t hal_i2c_write_u8(const hal_i2c_bus_t* bus, uint8_t dev_addr,
                                                uint8_t reg_addr, uint8_t value)
{
    return hal_i2c_write_reg(bus, dev_addr, reg_addr, &value, 1);
}

#endif  // HAL_I2C_H
