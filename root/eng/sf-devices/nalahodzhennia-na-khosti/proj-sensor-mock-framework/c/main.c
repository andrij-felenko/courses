#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

/* --- 1. Апаратний інтерфейс HAL I2C --- */
typedef enum {
    HAL_I2C_OK = 0,
    HAL_I2C_ERR_NACK = -1,
    HAL_I2C_ERR_TIMEOUT = -2,
    HAL_I2C_ERR_BUS = -3
} hal_i2c_status_t;

typedef struct hal_i2c_bus {
    hal_i2c_status_t (*write_read)(struct hal_i2c_bus *bus, uint8_t addr,
                                   const uint8_t *tx, size_t tx_len,
                                   uint8_t *rx, size_t rx_len);
    void *user_ctx;
} hal_i2c_bus_t;

/* --- 2. Емулятор периферійного давача (Mock) --- */
#define SENSOR_I2C_ADDR      0x68
#define REG_CHIP_ID          0x00
#define REG_STATUS           0x01
#define REG_TEMP_MSB         0x02
#define REG_TEMP_LSB         0x03
#define REG_CALIB_OFFSET     0x04
#define REG_RESET_CMD        0x0F

#define EXPECTED_CHIP_ID     0x5A

typedef struct {
    uint8_t registers[256];
    bool inject_nack;
    bool inject_timeout;
    uint32_t transaction_count;
} mock_sensor_ctx_t;

static hal_i2c_status_t mock_i2c_write_read(hal_i2c_bus_t *bus, uint8_t addr,
                                            const uint8_t *tx, size_t tx_len,
                                            uint8_t *rx, size_t rx_len) {
    mock_sensor_ctx_t *ctx = (mock_sensor_ctx_t *)bus->user_ctx;
    ctx->transaction_count++;

    if (addr != SENSOR_I2C_ADDR) {
        return HAL_I2C_ERR_NACK;
    }
    if (ctx->inject_nack) {
        return HAL_I2C_ERR_NACK;
    }
    if (ctx->inject_timeout) {
        return HAL_I2C_ERR_TIMEOUT;
    }
    if (tx_len == 0) {
        return HAL_I2C_ERR_BUS;
    }

    uint8_t reg_addr = tx[0];

    /* Якщо tx_len > 1 — це операція запису в регістри */
    if (tx_len > 1) {
        for (size_t i = 1; i < tx_len; ++i) {
            uint8_t target_reg = (uint8_t)(reg_addr + (i - 1));
            ctx->registers[target_reg] = tx[i];
            /* Обробка команди програмного скидання */
            if (target_reg == REG_RESET_CMD && tx[i] == 0xB6) {
                ctx->registers[REG_STATUS] = 0x00;
            }
        }
    }

    /* Якщо rx_len > 0 — це операція читання з автоінкрементом */
    if (rx_len > 0 && rx != NULL) {
        for (size_t i = 0; i < rx_len; ++i) {
            uint8_t target_reg = (uint8_t)(reg_addr + i);
            rx[i] = ctx->registers[target_reg];
        }
    }

    return HAL_I2C_OK;
}

void mock_sensor_init(mock_sensor_ctx_t *ctx, hal_i2c_bus_t *bus) {
    memset(ctx, 0, sizeof(*ctx));
    ctx->registers[REG_CHIP_ID] = EXPECTED_CHIP_ID;
    ctx->registers[REG_STATUS] = 0x01;       /* Дані готові */
    ctx->registers[REG_TEMP_MSB] = 0x09;     /* 0x09C4 = 2500 -> 25.00 C */
    ctx->registers[REG_TEMP_LSB] = 0xC4;
    ctx->registers[REG_CALIB_OFFSET] = 10;   /* Зміщення +0.10 C */

    bus->write_read = mock_i2c_write_read;
    bus->user_ctx = ctx;
}

/* --- 3. Драйвер давача (Тестований модуль) --- */
typedef struct {
    hal_i2c_bus_t *i2c;
    int32_t last_temperature_centi_c;
    int16_t calib_offset;
    bool is_initialized;
} sensor_driver_t;

typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_COMM = -1,
    DRIVER_ERR_WRONG_ID = -2,
    DRIVER_ERR_NOT_READY = -3
} driver_status_t;

driver_status_t sensor_driver_init(sensor_driver_t *drv, hal_i2c_bus_t *i2c) {
    drv->i2c = i2c;
    drv->is_initialized = false;
    drv->last_temperature_centi_c = 0;
    drv->calib_offset = 0;

    uint8_t tx_reg = REG_CHIP_ID;
    uint8_t chip_id = 0;
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, &chip_id, 1) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }
    if (chip_id != EXPECTED_CHIP_ID) {
        return DRIVER_ERR_WRONG_ID;
    }

    tx_reg = REG_CALIB_OFFSET;
    uint8_t calib_raw = 0;
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, &calib_raw, 1) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }
    drv->calib_offset = (int8_t)calib_raw;
    drv->is_initialized = true;
    return DRIVER_OK;
}

driver_status_t sensor_driver_read_temperature(sensor_driver_t *drv, int32_t *out_centi_c) {
    if (!drv->is_initialized) {
        return DRIVER_ERR_COMM;
    }

    uint8_t tx_reg = REG_STATUS;
    uint8_t status = 0;
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, &status, 1) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }
    if ((status & 0x01) == 0) {
        return DRIVER_ERR_NOT_READY;
    }

    tx_reg = REG_TEMP_MSB;
    uint8_t temp_raw_bytes[2] = {0};
    if (drv->i2c->write_read(drv->i2c, SENSOR_I2C_ADDR, &tx_reg, 1, temp_raw_bytes, 2) != HAL_I2C_OK) {
        return DRIVER_ERR_COMM;
    }

    int16_t raw_temp = (int16_t)((temp_raw_bytes[0] << 8) | temp_raw_bytes[1]);
    /* Температура в сотих градуса: Raw + Offset */
    int32_t temp_centi_c = (int32_t)raw_temp + (int32_t)drv->calib_offset;

    drv->last_temperature_centi_c = temp_centi_c;
    *out_centi_c = temp_centi_c;
    return DRIVER_OK;
}

/* --- 4. Тестові сценарії --- */
static void test_normal_initialization_and_read(void) {
    mock_sensor_ctx_t mock_ctx;
    hal_i2c_bus_t i2c_bus;
    mock_sensor_init(&mock_ctx, &i2c_bus);

    sensor_driver_t drv;
    driver_status_t status = sensor_driver_init(&drv, &i2c_bus);
    assert(status == DRIVER_OK);
    assert(drv.is_initialized == true);

    int32_t temperature = 0;
    status = sensor_driver_read_temperature(&drv, &temperature);
    assert(status == DRIVER_OK);
    /* Очікуємо 2500 + 10 = 2510 (25.10 C) */
    assert(temperature == 2510);
    printf("[PASS] test_normal_initialization_and_read\n");
}

static void test_sensor_nack_recovery(void) {
    mock_sensor_ctx_t mock_ctx;
    hal_i2c_bus_t i2c_bus;
    mock_sensor_init(&mock_ctx, &i2c_bus);

    mock_ctx.inject_nack = true;
    sensor_driver_t drv;
    driver_status_t status = sensor_driver_init(&drv, &i2c_bus);
    assert(status == DRIVER_ERR_COMM);
    assert(drv.is_initialized == false);
    printf("[PASS] test_sensor_nack_recovery\n");
}

int main(void) {
    printf("=== Запуск тестів драйвера на хості ===\n");
    test_normal_initialization_and_read();
    test_sensor_nack_recovery();
    printf("Всі тести виконано успішно.\n");
    return 0;
}
