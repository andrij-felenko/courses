/**
 * @file bus_adapters_c99.c
 * @brief Реалізація адаптерів I2C та SPI на C99.
 */

#include "bus_transaction_c99.h"
#include <string.h>

/* --- Реалізація операції Read-Modify-Write --- */
bus_status_t bus_modify_reg(const bus_interface_t *bus, uint16_t reg, uint8_t clear_mask, uint8_t set_mask) {
    uint8_t val = 0;
    bus_status_t st = bus_read_u8(bus, reg, &val);
    if (st != BUS_STATUS_OK) return st;

    uint8_t new_val = (val & ~clear_mask) | (set_mask & clear_mask);
    if (new_val == val) return BUS_STATUS_OK;

    return bus_write_u8(bus, reg, new_val);
}

/* =========================================================================
 * I2C Адаптер
 * ========================================================================= */
typedef struct {
    uint8_t  dev_addr;     /**< 7-бітна адреса I2C */
    void    *hal_handle;   /**< Дескриптор апаратного I2C */
} i2c_adapter_ctx_t;

extern int hal_i2c_write_read(void *hal, uint8_t addr, const uint8_t *tx, size_t tx_l, uint8_t *rx, size_t rx_l);
extern int hal_i2c_write(void *hal, uint8_t addr, const uint8_t *tx, size_t tx_l);

static bus_status_t i2c_read_impl(void *ctx, uint16_t reg, uint8_t *rx_buf, size_t len) {
    i2c_adapter_ctx_t *adapter = (i2c_adapter_ctx_t *)ctx;
    uint8_t reg_addr = (uint8_t)(reg & 0xFF);

    /* Атомарна операція: START -> DevAddr+W -> RegAddr -> Repeated START -> DevAddr+R -> Read -> STOP */
    int res = hal_i2c_write_read(adapter->hal_handle, adapter->dev_addr, &reg_addr, 1, rx_buf, len);
    return (res == 0) ? BUS_STATUS_OK : BUS_STATUS_ERR_IO;
}

static bus_status_t i2c_write_impl(void *ctx, uint16_t reg, const uint8_t *tx_buf, size_t len) {
    i2c_adapter_ctx_t *adapter = (i2c_adapter_ctx_t *)ctx;
    uint8_t buffer[64];
    if (len + 1 > sizeof(buffer)) return BUS_STATUS_ERR_PARAM;

    buffer[0] = (uint8_t)(reg & 0xFF);
    memcpy(&buffer[1], tx_buf, len);

    int res = hal_i2c_write(adapter->hal_handle, adapter->dev_addr, buffer, len + 1);
    return (res == 0) ? BUS_STATUS_OK : BUS_STATUS_ERR_IO;
}

static const bus_ops_t i2c_bus_ops = {
    .read_reg  = i2c_read_impl,
    .write_reg = i2c_write_impl,
    .lock      = NULL,
    .unlock    = NULL
};

void bus_init_i2c(bus_interface_t *bus, i2c_adapter_ctx_t *ctx, uint8_t addr, void *hal) {
    ctx->dev_addr   = addr;
    ctx->hal_handle = hal;
    bus->ops        = &i2c_bus_ops;
    bus->ctx        = ctx;
}

/* =========================================================================
 * SPI Адаптер
 * ========================================================================= */
typedef void (*spi_cs_fn)(bool select);

typedef struct {
    spi_cs_fn  cs_control;   /**< Функція керування піном CS */
    void      *hal_handle;   /**< Дескриптор апаратного SPI */
    bool       read_msb_flag;/**< Встановлювати біт 7 у '1' для операцій читання */
} spi_adapter_ctx_t;

extern int hal_spi_transfer(void *hal, const uint8_t *tx, uint8_t *rx, size_t len);

static bus_status_t spi_read_impl(void *ctx, uint16_t reg, uint8_t *rx_buf, size_t len) {
    spi_adapter_ctx_t *adapter = (spi_adapter_ctx_t *)ctx;
    uint8_t addr_byte = (uint8_t)(reg & 0x7F);
    if (adapter->read_msb_flag) {
        addr_byte |= 0x80; /* Встановлення біта читання SPI */
    }

    if (adapter->cs_control) adapter->cs_control(true); // CS Low

    uint8_t dummy = 0;
    int res = hal_spi_transfer(adapter->hal_handle, &addr_byte, &dummy, 1);
    if (res == 0) {
        res = hal_spi_transfer(adapter->hal_handle, NULL, rx_buf, len);
    }

    if (adapter->cs_control) adapter->cs_control(false); // CS High

    return (res == 0) ? BUS_STATUS_OK : BUS_STATUS_ERR_IO;
}

static bus_status_t spi_write_impl(void *ctx, uint16_t reg, const uint8_t *tx_buf, size_t len) {
    spi_adapter_ctx_t *adapter = (spi_adapter_ctx_t *)ctx;
    uint8_t addr_byte = (uint8_t)(reg & 0x7F); /* Біт 7 залишається '0' для запису */

    if (adapter->cs_control) adapter->cs_control(true);

    uint8_t dummy = 0;
    int res = hal_spi_transfer(adapter->hal_handle, &addr_byte, &dummy, 1);
    if (res == 0) {
        res = hal_spi_transfer(adapter->hal_handle, tx_buf, NULL, len);
    }

    if (adapter->cs_control) adapter->cs_control(false);

    return (res == 0) ? BUS_STATUS_OK : BUS_STATUS_ERR_IO;
}

static const bus_ops_t spi_bus_ops = {
    .read_reg  = spi_read_impl,
    .write_reg = spi_write_impl,
    .lock      = NULL,
    .unlock    = NULL
};

void bus_init_spi(bus_interface_t *bus, spi_adapter_ctx_t *ctx, spi_cs_fn cs, void *hal, bool read_msb) {
    ctx->cs_control    = cs;
    ctx->hal_handle    = hal;
    ctx->read_msb_flag = read_msb;
    bus->ops           = &spi_bus_ops;
    bus->ctx           = ctx;
}
