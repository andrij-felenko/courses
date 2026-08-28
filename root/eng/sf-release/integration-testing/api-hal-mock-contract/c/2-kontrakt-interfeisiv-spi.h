#ifndef HAL_INTERFACES_CONTRACT_H
#define HAL_INTERFACES_CONTRACT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_STATUS_OK = 0,
    HAL_STATUS_ERR_PARAM,
    HAL_STATUS_ERR_BUSY,
    HAL_STATUS_ERR_TIMEOUT,
    HAL_STATUS_ERR_NACK,
    HAL_STATUS_ERR_HARDWARE
} hal_status_t;

/* --- Інтерфейс драйвера GPIO --- */
typedef enum {
    HAL_GPIO_PIN_RESET = 0,
    HAL_GPIO_PIN_SET   = 1
} hal_gpio_state_t;

typedef struct hal_gpio_driver {
    void *ctx;
    hal_status_t (*write_pin)(void *ctx, uint16_t pin, hal_gpio_state_t state);
    hal_status_t (*read_pin)(void *ctx, uint16_t pin, hal_gpio_state_t *out_state);
    hal_status_t (*toggle_pin)(void *ctx, uint16_t pin);
} hal_gpio_driver_t;

/* --- Інтерфейс драйвера SPI --- */
typedef struct hal_spi_bus hal_spi_bus_t;
typedef void (*hal_spi_callback_t)(hal_spi_bus_t *bus, hal_status_t status, void *user_ctx);

struct hal_spi_bus {
    void *ctx;
    hal_status_t (*transfer_blocking)(void *ctx,
                                      const uint8_t *tx_buf,
                                      uint8_t *rx_buf,
                                      size_t length,
                                      uint32_t timeout_ms);
    hal_status_t (*transfer_async)(void *ctx,
                                   const uint8_t *tx_buf,
                                   uint8_t *rx_buf,
                                   size_t length,
                                   hal_spi_callback_t callback,
                                   void *user_ctx);
};

/* --- Інтерфейс драйвера I2C --- */
typedef struct hal_i2c_driver {
    void *ctx;
    hal_status_t (*mem_read)(void *ctx,
                             uint16_t dev_addr,
                             uint16_t mem_addr,
                             size_t mem_addr_size,
                             uint8_t *data,
                             size_t length,
                             uint32_t timeout_ms);
    hal_status_t (*master_transmit)(void *ctx,
                                    uint16_t dev_addr,
                                    const uint8_t *data,
                                    size_t length,
                                    uint32_t timeout_ms);
} hal_i2c_driver_t;

#endif /* HAL_INTERFACES_CONTRACT_H */
