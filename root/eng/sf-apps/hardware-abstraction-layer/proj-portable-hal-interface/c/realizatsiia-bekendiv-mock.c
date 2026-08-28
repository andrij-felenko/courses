#include "portable_hal_c99.h"
#include <string.h>

/* ========================================================================= */
/* 1. MOCK БЕКЕНД: Емуляція шин у пам'яті для модульного тестування           */
/* ========================================================================= */

#define MOCK_I2C_MEM_SIZE 256
#define MOCK_SPI_MEM_SIZE 1024

typedef struct {
    hal_gpio_level_t current_level;
    uint32_t toggle_count;
} mock_gpio_ctx_t;

static hal_status_t mock_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    (void)cfg;
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    ctx->current_level = HAL_GPIO_LEVEL_LOW;
    ctx->toggle_count = 0;
    return HAL_STATUS_OK;
}

static hal_status_t mock_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    ctx->current_level = level;
    return HAL_STATUS_OK;
}

static hal_status_t mock_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    *out_level = ctx->current_level;
    return HAL_STATUS_OK;
}

static hal_status_t mock_gpio_toggle(const hal_gpio_pin_t *pin) {
    mock_gpio_ctx_t *ctx = (mock_gpio_ctx_t *)pin->ctx;
    ctx->current_level = (ctx->current_level == HAL_GPIO_LEVEL_LOW) ? HAL_GPIO_LEVEL_HIGH : HAL_GPIO_LEVEL_LOW;
    ctx->toggle_count++;
    return HAL_STATUS_OK;
}

static const hal_gpio_ops_t mock_gpio_ops = {
    .init = mock_gpio_init,
    .set_level = mock_gpio_set,
    .get_level = mock_gpio_get,
    .toggle = mock_gpio_toggle
};

typedef struct {
    uint8_t registers[MOCK_I2C_MEM_SIZE];
    uint8_t expected_addr;
    bool force_nack;
} mock_i2c_ctx_t;

static hal_status_t mock_i2c_write(const hal_i2c_bus_t *bus, uint8_t addr,
                                   const uint8_t *tx, size_t len, uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_ctx_t *ctx = (mock_i2c_ctx_t *)bus->ctx;
    if (ctx->force_nack || addr != ctx->expected_addr) return HAL_STATUS_NACK;
    if (len < 1) return HAL_STATUS_INVALID_ARG;

    uint8_t reg = tx[0];
    for (size_t i = 1; i < len; ++i) {
        if ((size_t)(reg + i - 1) < MOCK_I2C_MEM_SIZE) {
            ctx->registers[reg + i - 1] = tx[i];
        }
    }
    return HAL_STATUS_OK;
}

static hal_status_t mock_i2c_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                  uint8_t *rx, size_t len, uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_ctx_t *ctx = (mock_i2c_ctx_t *)bus->ctx;
    if (ctx->force_nack || addr != ctx->expected_addr) return HAL_STATUS_NACK;

    for (size_t i = 0; i < len; ++i) {
        rx[i] = (i < MOCK_I2C_MEM_SIZE) ? ctx->registers[i] : 0xFF;
    }
    return HAL_STATUS_OK;
}

static hal_status_t mock_i2c_write_read(const hal_i2c_bus_t *bus, uint8_t addr,
                                        const uint8_t *tx, size_t tx_len,
                                        uint8_t *rx, size_t rx_len, uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_ctx_t *ctx = (mock_i2c_ctx_t *)bus->ctx;
    if (ctx->force_nack || addr != ctx->expected_addr) return HAL_STATUS_NACK;
    if (tx_len < 1) return HAL_STATUS_INVALID_ARG;

    uint8_t start_reg = tx[0];
    for (size_t i = 0; i < rx_len; ++i) {
        size_t idx = start_reg + i;
        rx[i] = (idx < MOCK_I2C_MEM_SIZE) ? ctx->registers[idx] : 0x00;
    }
    return HAL_STATUS_OK;
}

static const hal_i2c_ops_t mock_i2c_ops = {
    .write = mock_i2c_write,
    .read = mock_i2c_read,
    .write_read = mock_i2c_write_read
};

typedef struct {
    uint8_t flash_memory[MOCK_SPI_MEM_SIZE];
} mock_spi_ctx_t;

static hal_status_t mock_spi_transfer(const hal_spi_bus_t *bus,
                                      const uint8_t *tx, uint8_t *rx,
                                      size_t len, uint32_t timeout_ms) {
    (void)bus; (void)timeout_ms;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte_in = tx ? tx[i] : 0xFF;
        if (rx) rx[i] = byte_in;
    }
    return HAL_STATUS_OK;
}

static hal_status_t mock_spi_write(const hal_spi_bus_t *bus,
                                   const uint8_t *tx, size_t len, uint32_t timeout_ms) {
    return mock_spi_transfer(bus, tx, NULL, len, timeout_ms);
}

static hal_status_t mock_spi_read(const hal_spi_bus_t *bus,
                                  uint8_t *rx, size_t len, uint32_t timeout_ms) {
    return mock_spi_transfer(bus, NULL, rx, len, timeout_ms);
}

static const hal_spi_ops_t mock_spi_ops = {
    .transfer = mock_spi_transfer,
    .write = mock_spi_write,
    .read = mock_spi_read
};

/* ========================================================================= */
/* 2. STM32 БЕКЕНД: Пряма робота з регістрами Cortex-M (BSRR, ODR, IDR, I2C) */
/* ========================================================================= */

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} stm32_gpio_reg_t;

typedef struct {
    stm32_gpio_reg_t *port;
    uint8_t pin_num;
} stm32_gpio_ctx_t;

static hal_status_t stm32_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    if (!ctx || !ctx->port || ctx->pin_num > 15) return HAL_STATUS_INVALID_ARG;

    uint32_t pin_idx = ctx->pin_num;
    stm32_gpio_reg_t *port = ctx->port;

    port->MODER &= ~(3U << (pin_idx * 2));
    if (cfg->mode == HAL_GPIO_MODE_OUTPUT_PP || cfg->mode == HAL_GPIO_MODE_OUTPUT_OD) {
        port->MODER |= (1U << (pin_idx * 2));
    }

    if (cfg->mode == HAL_GPIO_MODE_OUTPUT_OD) {
        port->OTYPER |= (1U << pin_idx);
    } else {
        port->OTYPER &= ~(1U << pin_idx);
    }

    port->PUPDR &= ~(3U << (pin_idx * 2));
    if (cfg->pull == HAL_GPIO_PULL_UP) {
        port->PUPDR |= (1U << (pin_idx * 2));
    } else if (cfg->pull == HAL_GPIO_PULL_DOWN) {
        port->PUPDR |= (2U << (pin_idx * 2));
    }

    return HAL_STATUS_OK;
}

static hal_status_t stm32_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    if (level == HAL_GPIO_LEVEL_HIGH) {
        ctx->port->BSRR = (1U << ctx->pin_num);
    } else {
        ctx->port->BSRR = (1U << (ctx->pin_num + 16));
    }
    return HAL_STATUS_OK;
}

static hal_status_t stm32_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    *out_level = (ctx->port->IDR & (1U << ctx->pin_num)) ? HAL_GPIO_LEVEL_HIGH : HAL_GPIO_LEVEL_LOW;
    return HAL_STATUS_OK;
}

static hal_status_t stm32_gpio_toggle(const hal_gpio_pin_t *pin) {
    stm32_gpio_ctx_t *ctx = (stm32_gpio_ctx_t *)pin->ctx;
    ctx->port->ODR ^= (1U << ctx->pin_num);
    return HAL_STATUS_OK;
}

static const hal_gpio_ops_t stm32_gpio_ops = {
    .init = stm32_gpio_init,
    .set_level = stm32_gpio_set,
    .get_level = stm32_gpio_get,
    .toggle = stm32_gpio_toggle
};

/* ========================================================================= */
/* 3. RP2040 БЕКЕНД: Робота з атомарними апаратними регістрами SIO / GPIO    */
/* ========================================================================= */

typedef struct {
    volatile uint32_t GPIO_IN;
    volatile uint32_t GPIO_IN_HI;
    volatile uint32_t GPIO_OUT;
    volatile uint32_t GPIO_OUT_SET;
    volatile uint32_t GPIO_OUT_CLR;
    volatile uint32_t GPIO_OUT_XOR;
    volatile uint32_t GPIO_OE;
    volatile uint32_t GPIO_OE_SET;
    volatile uint32_t GPIO_OE_CLR;
    volatile uint32_t GPIO_OE_XOR;
} rp2040_sio_reg_t;

typedef struct {
    rp2040_sio_reg_t *sio;
    uint8_t pin_num;
} rp2040_gpio_ctx_t;

static hal_status_t rp2040_gpio_init(const hal_gpio_pin_t *pin, const hal_gpio_config_t *cfg) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    if (!ctx || !ctx->sio || ctx->pin_num > 29) return HAL_STATUS_INVALID_ARG;

    uint32_t mask = (1U << ctx->pin_num);
    if (cfg->mode == HAL_GPIO_MODE_OUTPUT_PP || cfg->mode == HAL_GPIO_MODE_OUTPUT_OD) {
        ctx->sio->GPIO_OE_SET = mask;
    } else {
        ctx->sio->GPIO_OE_CLR = mask;
    }
    return HAL_STATUS_OK;
}

static hal_status_t rp2040_gpio_set(const hal_gpio_pin_t *pin, hal_gpio_level_t level) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    uint32_t mask = (1U << ctx->pin_num);
    if (level == HAL_GPIO_LEVEL_HIGH) {
        ctx->sio->GPIO_OUT_SET = mask;
    } else {
        ctx->sio->GPIO_OUT_CLR = mask;
    }
    return HAL_STATUS_OK;
}

static hal_status_t rp2040_gpio_get(const hal_gpio_pin_t *pin, hal_gpio_level_t *out_level) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    *out_level = (ctx->sio->GPIO_IN & (1U << ctx->pin_num)) ? HAL_GPIO_LEVEL_HIGH : HAL_GPIO_LEVEL_LOW;
    return HAL_STATUS_OK;
}

static hal_status_t rp2040_gpio_toggle(const hal_gpio_pin_t *pin) {
    rp2040_gpio_ctx_t *ctx = (rp2040_gpio_ctx_t *)pin->ctx;
    ctx->sio->GPIO_OUT_XOR = (1U << ctx->pin_num);
    return HAL_STATUS_OK;
}

static const hal_gpio_ops_t rp2040_gpio_ops = {
    .init = rp2040_gpio_init,
    .set_level = rp2040_gpio_set,
    .get_level = rp2040_gpio_get,
    .toggle = rp2040_gpio_toggle
};
