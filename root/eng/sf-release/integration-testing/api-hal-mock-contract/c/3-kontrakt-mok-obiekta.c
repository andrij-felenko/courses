#include "hal_interfaces_contract.h"
#include <string.h>

#define MOCK_I2C_MAX_REGS 256

typedef struct {
    uint8_t registers[MOCK_I2C_MAX_REGS];
    uint16_t expected_dev_addr;
    hal_status_t injected_status;
    size_t call_count;
    uint8_t last_written_reg;
    uint8_t last_written_val;
} mock_i2c_context_t;

static hal_status_t mock_i2c_mem_read(void *ctx,
                                      uint16_t dev_addr,
                                      uint16_t mem_addr,
                                      size_t mem_addr_size,
                                      uint8_t *data,
                                      size_t length,
                                      uint32_t timeout_ms) {
    (void)mem_addr_size;
    (void)timeout_ms;
    mock_i2c_context_t *mock = (mock_i2c_context_t *)ctx;
    mock->call_count++;

    if (mock->injected_status != HAL_STATUS_OK) {
        hal_status_t status = mock->injected_status;
        mock->injected_status = HAL_STATUS_OK;
        return status;
    }

    if (dev_addr != mock->expected_dev_addr) {
        return HAL_STATUS_ERR_NACK;
    }

    for (size_t i = 0; i < length; ++i) {
        uint16_t reg_idx = (mem_addr + i) % MOCK_I2C_MAX_REGS;
        data[i] = mock->registers[reg_idx];
    }

    return HAL_STATUS_OK;
}

static hal_status_t mock_i2c_master_transmit(void *ctx,
                                             uint16_t dev_addr,
                                             const uint8_t *data,
                                             size_t length,
                                             uint32_t timeout_ms) {
    (void)timeout_ms;
    mock_i2c_context_t *mock = (mock_i2c_context_t *)ctx;
    mock->call_count++;

    if (mock->injected_status != HAL_STATUS_OK) {
        return mock->injected_status;
    }

    if (dev_addr != mock->expected_dev_addr) {
        return HAL_STATUS_ERR_NACK;
    }

    if (length >= 2) {
        uint8_t reg_addr = data[0];
        uint8_t reg_val = data[1];
        mock->registers[reg_addr] = reg_val;
        mock->last_written_reg = reg_addr;
        mock->last_written_val = reg_val;
    }

    return HAL_STATUS_OK;
}

void mock_i2c_init(mock_i2c_context_t *mock, uint16_t dev_addr, hal_i2c_driver_t *out_driver) {
    memset(mock, 0, sizeof(mock_i2c_context_t));
    mock->expected_dev_addr = dev_addr;
    mock->injected_status = HAL_STATUS_OK;

    out_driver->ctx = mock;
    out_driver->mem_read = mock_i2c_mem_read;
    out_driver->master_transmit = mock_i2c_master_transmit;
}
