/* i2c_driver.h - Публічний файл інтерфейсу C99 */
#ifndef I2C_DRIVER_H
#define I2C_DRIVER_H

#include <stdint.h>
#include <stddef.h>

typedef struct i2c_driver_context_s i2c_driver_t; /* Неповний тип */
typedef i2c_driver_t* i2c_handle_t;               /* Непрозорий дескриптор */

typedef struct {
    uint32_t clock_speed_hz;
    uint16_t timeout_ms;
} i2c_user_config_t;

/* Публічні операції */
i2c_handle_t i2c_create_instance(uint8_t port_index, const i2c_user_config_t* config);
int i2c_transfer(i2c_handle_t handle, uint8_t addr, const uint8_t* tx, size_t tx_len, uint8_t* rx, size_t rx_len);

#endif
