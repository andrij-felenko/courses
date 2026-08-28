#ifndef PORTABLE_HAL_C99_H
#define PORTABLE_HAL_C99_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Уніфіковані коди помилок периферійного шару */
typedef enum {
    HAL_STATUS_OK              =  0,
    HAL_STATUS_ERROR           = -1,
    HAL_STATUS_TIMEOUT         = -2,
    HAL_STATUS_BUSY            = -3,
    HAL_STATUS_NACK            = -4,
    HAL_STATUS_INVALID_ARG     = -5,
    HAL_STATUS_NOT_SUPPORTED   = -6
} hal_status_t;

/* Логічний рівень цифрової лінії */
typedef enum {
    HAL_GPIO_LEVEL_LOW  = 0,
    HAL_GPIO_LEVEL_HIGH = 1
} hal_gpio_level_t;

/* Режим роботи цифрової лінії */
typedef enum {
    HAL_GPIO_MODE_INPUT,
    HAL_GPIO_MODE_OUTPUT_PP,
    HAL_GPIO_MODE_OUTPUT_OD
} hal_gpio_mode_t;

/* Підтяжка цифрової лінії */
typedef enum {
    HAL_GPIO_PULL_NONE,
    HAL_GPIO_PULL_UP,
    HAL_GPIO_PULL_DOWN
} hal_gpio_pull_t;

/* Конфігурація лінії GPIO */
typedef struct {
    hal_gpio_mode_t mode;
    hal_gpio_pull_t pull;
} hal_gpio_config_t;

/* Таблиця операцій GPIO */
struct hal_gpio_pin;
typedef struct {
    hal_status_t (*init)(const struct hal_gpio_pin *pin, const hal_gpio_config_t *cfg);
    hal_status_t (*set_level)(const struct hal_gpio_pin *pin, hal_gpio_level_t level);
    hal_status_t (*get_level)(const struct hal_gpio_pin *pin, hal_gpio_level_t *out_level);
    hal_status_t (*toggle)(const struct hal_gpio_pin *pin);
} hal_gpio_ops_t;

/* Дескриптор лінії GPIO */
typedef struct hal_gpio_pin {
    const hal_gpio_ops_t *ops;
    void *ctx;
} hal_gpio_pin_t;

/* Зручні функції-обгортки для клієнтського коду */
static inline hal_status_t hal_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    if (!pin || !pin->ops || !pin->ops->init) return HAL_STATUS_INVALID_ARG;
    return pin->ops->init(pin, cfg);
}

static inline hal_status_t hal_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    if (!pin || !pin->ops || !pin->ops->set_level) return HAL_STATUS_INVALID_ARG;
    return pin->ops->set_level(pin, level);
}

static inline hal_status_t hal_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    if (!pin || !pin->ops || !pin->ops->get_level || !out_level) return HAL_STATUS_INVALID_ARG;
    return pin->ops->get_level(pin, out_level);
}

static inline hal_status_t hal_gpio_toggle(const hal_gpio_pin_t *pin) {
    if (!pin || !pin->ops || !pin->ops->toggle) return HAL_STATUS_INVALID_ARG;
    return pin->ops->toggle(pin);
}

/* Інтерфейс магістралі I2C */
struct hal_i2c_bus;
typedef struct {
    hal_status_t (*write)(const struct hal_i2c_bus *bus, uint8_t addr_7bit,
                          const uint8_t *tx_data, size_t len, uint32_t timeout_ms);
    hal_status_t (*read)(const struct hal_i2c_bus *bus, uint8_t addr_7bit,
                         uint8_t *rx_data, size_t len, uint32_t timeout_ms);
    hal_status_t (*write_read)(const struct hal_i2c_bus *bus, uint8_t addr_7bit,
                              const uint8_t *tx_data, size_t tx_len,
                              uint8_t *rx_data, size_t rx_len, uint32_t timeout_ms);
} hal_i2c_ops_t;

typedef struct hal_i2c_bus {
    const hal_i2c_ops_t *ops;
    void *ctx;
} hal_i2c_bus_t;

static inline hal_status_t hal_i2c_write(const hal_i2c_bus_t *bus, uint8_t addr,
                                         const uint8_t *data, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->write) return HAL_STATUS_INVALID_ARG;
    return bus->ops->write(bus, addr, data, len, timeout_ms);
}

static inline hal_status_t hal_i2c_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                        uint8_t *data, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->read) return HAL_STATUS_INVALID_ARG;
    return bus->ops->read(bus, addr, data, len, timeout_ms);
}

static inline hal_status_t hal_i2c_write_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                              const uint8_t *tx, size_t tx_len,
                                              uint8_t *rx, size_t rx_len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->write_read) return HAL_STATUS_INVALID_ARG;
    return bus->ops->write_read(bus, addr, tx, tx_len, rx, rx_len, timeout_ms);
}

/* Інтерфейс магістралі SPI */
struct hal_spi_bus;
typedef struct {
    hal_status_t (*transfer)(const struct hal_spi_bus *bus,
                            const uint8_t *tx_buf, uint8_t *rx_buf,
                            size_t len, uint32_t timeout_ms);
    hal_status_t (*write)(const struct hal_spi_bus *bus,
                          const uint8_t *tx_buf, size_t len, uint32_t timeout_ms);
    hal_status_t (*read)(const struct hal_spi_bus *bus,
                         uint8_t *rx_buf, size_t len, uint32_t timeout_ms);
} hal_spi_ops_t;

typedef struct hal_spi_bus {
    const hal_spi_ops_t *ops;
    void *ctx;
} hal_spi_bus_t;

static inline hal_status_t hal_spi_transfer(const hal_spi_bus_t *bus,
                                            const uint8_t *tx, uint8_t *rx,
                                            size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->transfer) return HAL_STATUS_INVALID_ARG;
    return bus->ops->transfer(bus, tx, rx, len, timeout_ms);
}

static inline hal_status_t hal_spi_write(const hal_spi_bus_t *bus,
                                         const uint8_t *tx, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->write) return HAL_STATUS_INVALID_ARG;
    return bus->ops->write(bus, tx, len, timeout_ms);
}

static inline hal_status_t hal_spi_read(const hal_spi_bus_t *bus,
                                        uint8_t *rx, size_t len, uint32_t timeout_ms) {
    if (!bus || !bus->ops || !bus->ops->read) return HAL_STATUS_INVALID_ARG;
    return bus->ops->read(bus, rx, len, timeout_ms);
}

#endif /* PORTABLE_HAL_C99_H */
