#ifndef I2C_BUS_H
#define I2C_BUS_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file i2c_bus.h
 * @brief Оголошення абстракції апаратного шинного інтерфейсу I2C.
 */

/**
 * @brief Коди помилок шинного інтерфейсу I2C.
 */
typedef enum {
    I2C_SUCCESS           =  0, /**< Операцію виконано успішно */
    I2C_ERR_NACK          = -1, /**< Отримано NACK від веденого пристрою */
    I2C_ERR_BUSY          = -2, /**< Шина зайнята */
    I2C_ERR_TIMEOUT       = -3, /**< Перевищено тайм-аут ожидання */
    I2C_ERR_INVALID_ARG   = -4, /**< Некоректні вхідні аргументи */
    I2C_ERR_HARDWARE_FAIL = -5  /**< Апаратний збій шини */
} i2c_err_t;

/**
 * @brief Структура конфігурації апаратного порту I2C.
 */
typedef struct {
    uint8_t i2c_port;          /**< Номер порту I2C */
    uint32_t clock_speed_hz;   /**< Частота тактування в Гц */
    uint32_t timeout_ms;       /**< Базовий тайм-аут у мс */
    bool enable_clock_stretch; /**< Прапорець підтримки Clock Stretching */
} i2c_bus_config_t;

/**
 * @brief Ініціалізація шини I2C хоста.
 */
i2c_err_t i2c_bus_init(const i2c_bus_config_t *config);

/**
 * @brief Передача буфера байтів пристрою по I2C.
 */
i2c_err_t i2c_bus_write(uint8_t dev_addr, const uint8_t *data, size_t len, uint32_t timeout_ms);

/**
 * @brief Зчитування буфера байтів із пристрою по I2C.
 */
i2c_err_t i2c_bus_read(uint8_t dev_addr, uint8_t *buffer, size_t len, uint32_t timeout_ms);

/**
 * @brief Комбінована транзакція: запис команди та наступне зчитування відповіді.
 */
i2c_err_t i2c_bus_write_read(uint8_t dev_addr,
                             const uint8_t *tx_data, size_t tx_len,
                             uint8_t *rx_buffer, size_t rx_len,
                             uint32_t delay_ms, uint32_t timeout_ms);

#endif /* I2C_BUS_H */
