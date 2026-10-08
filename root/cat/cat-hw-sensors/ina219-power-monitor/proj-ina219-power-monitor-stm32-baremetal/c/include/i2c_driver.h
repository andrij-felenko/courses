#ifndef I2C_DRIVER_H
#define I2C_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file i2c_driver.h
 * @brief Низькорівневий bare-metal інтерфейс I2C для мікроконтролерів STM32.
 */

/**
 * @brief Коди помилок шини I2C.
 */
typedef enum {
    I2C_OK = 0,            /* Операція виконана успішно */
    I2C_ERR_BUSY,          /* Шина зайнята */
    I2C_ERR_START_FAIL,    /* Помилка генерації START умови */
    I2C_ERR_ADDR_NACK,     /* Відсутність підтвердження адреси (ACK Failure) */
    I2C_ERR_DATA_NACK,     /* Відсутність підтвердження даних */
    I2C_ERR_TIMEOUT,       /* Таймаут очікування апаратних прапорців */
    I2C_ERR_PARAM          /* Некоректні вхідні аргументи */
} i2c_status_t;

/**
 * @brief Апаратна карта регістрів I2C периферії STM32 (I2C1/I2C2).
 */
typedef struct {
    volatile uint32_t CR1;   /* Control Register 1 */
    volatile uint32_t CR2;   /* Control Register 2 */
    volatile uint32_t OAR1;  /* Own Address Register 1 */
    volatile uint32_t OAR2;  /* Own Address Register 2 */
    volatile uint32_t DR;    /* Data Register */
    volatile uint32_t SR1;   /* Status Register 1 */
    volatile uint32_t SR2;   /* Status Register 2 */
    volatile uint32_t CCR;   /* Clock Control Register */
    volatile uint32_t TRISE; /* Rise Time Register */
    volatile uint32_t FLTR;  /* Filter Register (для новіших серій) */
} i2c_reg_t;

/**
 * @brief Дескриптор шини I2C.
 */
typedef struct {
    i2c_reg_t *instance;     /* Вказівник на базову адресу регістрів I2C */
    uint32_t timeout_cycles; /* Кількість ітерацій таймауту */
    uint32_t pclk1_freq_hz;  /* Частота тактування периферійної шини APB1 */
    uint32_t i2c_speed_hz;   /* Цільова частота SCL (100000 або 400000 Гц) */
} i2c_bus_t;

/* Прототипи процедур прямого керування периферією I2C */
i2c_status_t i2c_init(i2c_bus_t *bus, i2c_reg_t *instance, uint32_t pclk1_hz, uint32_t i2c_speed_hz);
i2c_status_t i2c_start(i2c_bus_t *bus);
i2c_status_t i2c_stop(i2c_bus_t *bus);
i2c_status_t i2c_write_addr(i2c_bus_t *bus, uint8_t dev_addr, bool is_read);
i2c_status_t i2c_write_bytes(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, size_t len);
i2c_status_t i2c_read_bytes(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, size_t len);
i2c_status_t i2c_write_reg16(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint16_t value);
i2c_status_t i2c_read_reg16(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint16_t *value);

#endif /* I2C_DRIVER_H */
