/**
 * @file bus_adapters.c
 * @brief Реалізація адаптерів I2C, SPI та Mock у мові C99.
 */

#include "bus_transaction.h"
#include <string.h>

/* ============================================================================
 * Реалізація універсальної операції Read-Modify-Write
 * ============================================================================ */

bus_status_t bus_modify_reg(const bus_interface_t *bus, uint16_t reg, uint8_t mask, uint8_t val) {
    if (!bus) return BUS_ERR_INVALID_ARG;
    
    uint8_t current_val = 0;
    bus_status_t status = bus_read_u8(bus, reg, &current_val);
    if (status != BUS_OK) {
        return status;
    }

    uint8_t new_val = (current_val & ~mask) | (val & mask);
    if (new_val == current_val) {
        return BUS_OK; /* Значення вже встановлено, уникаємо зайвої транзакції */
    }

    return bus_write_u8(bus, reg, new_val);
}

/* ============================================================================
 * I2C Адаптер (I2C Adapter Context & Operations)
 * ============================================================================ */

typedef struct {
    uint8_t  dev_addr_7bit; /**< 7-бітна адреса пристрою на шині I2C */
    uint32_t timeout_ms;    /**< Таймаут виконання апаратної транзакції */
    void    *i2c_hal_handle;/**< Дескриптор апаратного контролера I2C */
} i2c_adapter_ctx_t;

/* Низькорівневі виклики емульованого HAL мікроконтролера */
extern int hal_i2c_master_transmit(void *handle, uint8_t addr, const uint8_t *data, size_len_t len, uint32_t timeout);
extern int hal_i2c_master_write_read(void *handle, uint8_t addr, const uint8_t *tx, size_t tx_len, uint8_t *rx, size_t rx_len, uint32_t timeout);

static bus_status_t i2c_read_reg_impl(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len) {
    i2c_adapter_ctx_t *adapter = (i2c_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    uint8_t reg_buf[2];
    size_t reg_len = 1;
    reg_buf[0] = (uint8_t)(reg_addr & 0xFF);

    /* Якщо адреса 16-бітна, надсилаємо старший байт першим (Big Endian) */
    if (reg_addr > 0xFF) {
        reg_buf[0] = (uint8_t)((reg_addr >> 8) & 0xFF);
        reg_buf[1] = (uint8_t)(reg_addr & 0xFF);
        reg_len = 2;
    }

    /* Атомарна I2C транзакція: START -> DevAddr+W -> RegAddr -> RepSTART -> DevAddr+R -> Data -> STOP */
    int res = hal_i2c_master_write_read(adapter->i2c_hal_handle, adapter->dev_addr_7bit,
                                        reg_buf, reg_len, data, len, adapter->timeout_ms);
    if (res == 0) return BUS_OK;
    if (res == -2) return BUS_ERR_NACK;
    if (res == -3) return BUS_ERR_TIMEOUT;
    return BUS_ERR_IO;
}

static bus_status_t i2c_write_reg_impl(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len) {
    i2c_adapter_ctx_t *adapter = (i2c_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    /* Об'єднуємо адресу регістра та байти даних у єдиний буфер передачі */
    uint8_t tx_buffer[64];
    size_t header_len = (reg_addr > 0xFF) ? 2 : 1;
    if (header_len + len > sizeof(tx_buffer)) {
        return BUS_ERR_INVALID_ARG;
    }

    if (header_len == 1) {
        tx_buffer[0] = (uint8_t)(reg_addr & 0xFF);
    } else {
        tx_buffer[0] = (uint8_t)((reg_addr >> 8) & 0xFF);
        tx_buffer[1] = (uint8_t)(reg_addr & 0xFF);
    }
    memcpy(&tx_buffer[header_len], data, len);

    int res = hal_i2c_master_transmit(adapter->i2c_hal_handle, adapter->dev_addr_7bit,
                                      tx_buffer, header_len + len, adapter->timeout_ms);
    if (res == 0) return BUS_OK;
    if (res == -2) return BUS_ERR_NACK;
    if (res == -3) return BUS_ERR_TIMEOUT;
    return BUS_ERR_IO;
}

static bus_status_t i2c_lock_impl(void *ctx, uint32_t timeout_ms) {
    (void)ctx; (void)timeout_ms;
    return BUS_OK; /* Вбудовується виклик xSemaphoreTake у середовищі FreeRTOS */
}

static bus_status_t i2c_unlock_impl(void *ctx) {
    (void)ctx;
    return BUS_OK; /* Вбудовується виклик xSemaphoreGive */
}

static const bus_ops_t i2c_bus_ops = {
    .read_reg  = i2c_read_reg_impl,
    .write_reg = i2c_write_reg_impl,
    .transfer  = NULL,
    .lock      = i2c_lock_impl,
    .unlock    = i2c_unlock_impl
};

void bus_init_i2c_interface(bus_interface_t *bus, i2c_adapter_ctx_t *ctx, uint8_t dev_addr, void *hal_handle) {
    ctx->dev_addr_7bit   = dev_addr;
    ctx->timeout_ms      = 100;
    ctx->i2c_hal_handle  = hal_handle;

    bus->ops   = &i2c_bus_ops;
    bus->ctx   = ctx;
    bus->flags = BUS_FLAG_NONE;
}

/* ============================================================================
 * SPI Адаптер (SPI Adapter Context & Operations)
 * ============================================================================ */

typedef void (*spi_cs_ctrl_fn)(bool active);

typedef struct {
    spi_cs_ctrl_fn  cs_ctrl;       /**< Функція керування лінією Chip Select */
    void           *spi_hal_handle;/**< Дескриптор апаратного SPI периферійного блоку */
    uint32_t        flags;         /**< Прапорці модифікації адресного байта */
    uint32_t        timeout_ms;
} spi_adapter_ctx_t;

extern int hal_spi_transfer_sync(void *handle, const uint8_t *tx, uint8_t *rx, size_t len, uint32_t timeout);

static bus_status_t spi_read_reg_impl(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len) {
    spi_adapter_ctx_t *adapter = (spi_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    uint8_t addr_byte = (uint8_t)(reg_addr & 0x7F);

    /* Застосування специфічних прапорців шини SPI для датчиків */
    if (adapter->flags & BUS_FLAG_SPI_READ_MSB) {
        addr_byte |= 0x80; /* Встановлюємо біт 7 у '1' для читання */
    }
    if (adapter->flags & BUS_FLAG_AUTO_INC) {
        addr_byte |= 0x40; /* Встановлюємо біт 6 у '1' для автоінкременту (LSM6DSO) */
    }

    /* Активація Chip Select (активний низький рівень) */
    if (adapter->cs_ctrl) adapter->cs_ctrl(true);

    /* Надсилаємо байт адреси регістра */
    uint8_t dummy_rx = 0;
    int res = hal_spi_transfer_sync(adapter->spi_hal_handle, &addr_byte, &dummy_rx, 1, adapter->timeout_ms);
    if (res != 0) {
        if (adapter->cs_ctrl) adapter->cs_ctrl(false);
        return BUS_ERR_IO;
    }

    /* Якщо потрібен dummy-байт для високих швидкостей SCK */
    if (adapter->flags & BUS_FLAG_USE_DUMMY) {
        uint8_t dummy_tx = 0x00;
        hal_spi_transfer_sync(adapter->spi_hal_handle, &dummy_tx, &dummy_rx, 1, adapter->timeout_ms);
    }

    /* Зчитування корисних даних: надсилаємо нулі, зчитуємо байти з MISO */
    uint8_t dummy_tx_buf[64] = {0};
    res = hal_spi_transfer_sync(adapter->spi_hal_handle, dummy_tx_buf, data, len, adapter->timeout_ms);

    /* Деактивація Chip Select */
    if (adapter->cs_ctrl) adapter->cs_ctrl(false);

    return (res == 0) ? BUS_OK : BUS_ERR_IO;
}

static bus_status_t spi_write_reg_impl(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len) {
    spi_adapter_ctx_t *adapter = (spi_adapter_ctx_t *)ctx;
    if (!adapter || !data || len == 0) return BUS_ERR_INVALID_ARG;

    uint8_t addr_byte = (uint8_t)(reg_addr & 0x7F); /* Біт 7 залишається '0' для запису */
    if (adapter->flags & BUS_FLAG_AUTO_INC) {
        addr_byte |= 0x40;
    }

    if (adapter->cs_ctrl) adapter->cs_ctrl(true);

    /* Передача адреси */
    uint8_t dummy_rx = 0;
    int res = hal_spi_transfer_sync(adapter->spi_hal_handle, &addr_byte, &dummy_rx, 1, adapter->timeout_ms);
    if (res == 0) {
        /* Передача тіла даних */
        res = hal_spi_transfer_sync(adapter->spi_hal_handle, data, NULL, len, adapter->timeout_ms);
    }

    if (adapter->cs_ctrl) adapter->cs_ctrl(false);

    return (res == 0) ? BUS_OK : BUS_ERR_IO;
}

static const bus_ops_t spi_bus_ops = {
    .read_reg  = spi_read_reg_impl,
    .write_reg = spi_write_reg_impl,
    .transfer  = NULL,
    .lock      = NULL,
    .unlock    = NULL
};

void bus_init_spi_interface(bus_interface_t *bus, spi_adapter_ctx_t *ctx, spi_cs_ctrl_fn cs_fn, void *hal_handle, uint32_t flags) {
    ctx->cs_ctrl        = cs_fn;
    ctx->spi_hal_handle = hal_handle;
    ctx->flags          = flags;
    ctx->timeout_ms     = 100;

    bus->ops   = &spi_bus_ops;
    bus->ctx   = ctx;
    bus->flags = flags;
}

/* ============================================================================
 * Mock / Loopback Адаптер для Unit-тестування без заліза
 * ============================================================================ */

typedef struct {
    uint8_t registers[256];     /**< Віртуальний масив 256 регістрів */
    bool    simulate_nack;      /**< Прапорець емуляції обриву шини */
    size_t  read_transaction_cnt;
    size_t  write_transaction_cnt;
} mock_adapter_ctx_t;

static bus_status_t mock_read_reg_impl(void *ctx, uint16_t reg_addr, uint8_t *data, size_t len) {
    mock_adapter_ctx_t *mock = (mock_adapter_ctx_t *)ctx;
    if (!mock || !data) return BUS_ERR_INVALID_ARG;
    if (mock->simulate_nack) return BUS_ERR_NACK;
    if (reg_addr + len > sizeof(mock->registers)) return BUS_ERR_INVALID_ARG;

    memcpy(data, &mock->registers[reg_addr], len);
    mock->read_transaction_cnt++;
    return BUS_OK;
}

static bus_status_t mock_write_reg_impl(void *ctx, uint16_t reg_addr, const uint8_t *data, size_t len) {
    mock_adapter_ctx_t *mock = (mock_adapter_ctx_t *)ctx;
    if (!mock || !data) return BUS_ERR_INVALID_ARG;
    if (mock->simulate_nack) return BUS_ERR_NACK;
    if (reg_addr + len > sizeof(mock->registers)) return BUS_ERR_INVALID_ARG;

    memcpy(&mock->registers[reg_addr], data, len);
    mock->write_transaction_cnt++;
    return BUS_OK;
}

static const bus_ops_t mock_bus_ops = {
    .read_reg  = mock_read_reg_impl,
    .write_reg = mock_write_reg_impl,
    .transfer  = NULL,
    .lock      = NULL,
    .unlock    = NULL
};

void bus_init_mock_interface(bus_interface_t *bus, mock_adapter_ctx_t *ctx) {
    memset(ctx, 0, sizeof(mock_adapter_ctx_t));
    bus->ops   = &mock_bus_ops;
    bus->ctx   = ctx;
    bus->flags = BUS_FLAG_NONE;
}
