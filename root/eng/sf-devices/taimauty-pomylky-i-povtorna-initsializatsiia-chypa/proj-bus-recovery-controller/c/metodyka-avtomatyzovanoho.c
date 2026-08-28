#include <stdio.h>
#include <stdbool.h>
#include "stm32f4xx.h"
#include "dwt_timeout.h"
#include "i2c_bus_recovery.h"
#include "reset_escalation_controller.h"
#include "sensor_state_recovery.h"
#include "bus_diagnostics.h"

#define BMP280_I2C_ADDR 0x76
#define BMP280_CHIP_ID_REG 0xD0
#define BMP280_EXPECTED_ID 0x58
#define BMP280_RESET_REG 0xE0
#define BMP280_CTRL_MEAS_REG 0xF4
#define BMP280_CONFIG_REG 0xF5

typedef struct {
    reset_escalation_manager_t escalation;
    sensor_shadow_cache_t shadow;
    bus_diagnostics_log_t diag_log;
    uint8_t i2c_addr;
} bmp280_resilient_driver_t;

int bmp280_raw_i2c_write(I2C_TypeDef *i2c, uint8_t addr, uint8_t reg, uint8_t val) {
    // 1. Очікуємо звільнення шини з таймаутом 2 мс
    if (dwt_wait_register_bit(&i2c->SR2, I2C_SR2_BUSY, false, 2000) != 0) {
        return -1;
    }

    // 2. Генеруємо START
    i2c->CR1 |= I2C_CR1_START;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_SB, true, 2000) != 0) {
        return -2;
    }

    // 3. Відправляємо адресу пристрою (Write)
    i2c->DR = (uint8_t)(addr << 1);
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_ADDR, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -3; // NACK адреси
    }
    (void)i2c->SR2; // Очищення ADDR читанням SR2

    // 4. Відправляємо адресу регістра
    i2c->DR = reg;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_TXE, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -4;
    }

    // 5. Відправляємо дані
    i2c->DR = val;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_BTF, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -5;
    }

    // 6. Генеруємо STOP
    i2c->CR1 |= I2C_CR1_STOP;
    return 0;
}

int bmp280_raw_i2c_read(I2C_TypeDef *i2c, uint8_t addr, uint8_t reg, uint8_t *out_val) {
    if (dwt_wait_register_bit(&i2c->SR2, I2C_SR2_BUSY, false, 2000) != 0) return -1;

    i2c->CR1 |= I2C_CR1_START;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_SB, true, 2000) != 0) return -2;

    i2c->DR = (uint8_t)(addr << 1);
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_ADDR, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -3;
    }
    (void)i2c->SR2;

    i2c->DR = reg;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_TXE, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -4;
    }

    // Повторний старт (Repeated START)
    i2c->CR1 |= I2C_CR1_START;
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_SB, true, 2000) != 0) return -5;

    i2c->DR = (uint8_t)((addr << 1) | 1); // Read
    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_ADDR, true, 2000) != 0) {
        i2c->CR1 |= I2C_CR1_STOP;
        return -6;
    }
    i2c->CR1 &= ~I2C_CR1_ACK; // NACK перед останнім байтом
    (void)i2c->SR2;
    i2c->CR1 |= I2C_CR1_STOP;

    if (dwt_wait_register_bit(&i2c->SR1, I2C_SR1_RXNE, true, 2000) != 0) return -7;
    *out_val = (uint8_t)i2c->DR;

    return 0;
}

int bmp280_recover_and_restore(bmp280_resilient_driver_t *drv) {
    escalation_tier_t tier = escalation_step(&drv->escalation);
    diagnostics_log_record(&drv->diag_log, (bus_event_type_t)(EVENT_TIER1_SOFT_RESET + (tier - 1)), 1, -1, drv->escalation.consecutive_failures);

    if (tier == ESCALATION_TIER_FATAL) {
        return -100; // Фатальна відмова периферії
    }

    // Перевірка працездатності: зчитування ID
    uint8_t chip_id = 0;
    int res = bmp280_raw_i2c_read(drv->escalation.i2c_hw.i2c, drv->i2c_addr, BMP280_CHIP_ID_REG, &chip_id);
    if (res != 0 || chip_id != BMP280_EXPECTED_ID) {
        return -1; // Сенсор ще не готовий, вимагає подальшої ескалації
    }

    // Відновлення робочих регістрів із тіньового кешу
    for (uint8_t i = 0; i < drv->shadow.reg_count; i++) {
        bmp280_raw_i2c_write(drv->escalation.i2c_hw.i2c, drv->i2c_addr,
                             drv->shadow.registers[i].reg_addr,
                             drv->shadow.registers[i].value);
    }

    escalation_mark_success(&drv->escalation);
    diagnostics_log_record(&drv->diag_log, EVENT_RECOVERY_SUCCESS, 1, 0, 0);
    return 0;
}

int bmp280_init(bmp280_resilient_driver_t *drv, const peripheral_power_control_t *pwr, const i2c_bus_hardware_t *i2c_hw) {
    dwt_timer_global_init();
    escalation_manager_init(&drv->escalation, pwr, i2c_hw);
    shadow_cache_init(&drv->shadow);
    diagnostics_log_init(&drv->diag_log);
    drv->i2c_addr = BMP280_I2C_ADDR;

    // Конфігурація робочих параметрів
    shadow_cache_set_reg(&drv->shadow, BMP280_CTRL_MEAS_REG, 0x57); // Normal mode, OverSampling x16
    shadow_cache_set_reg(&drv->shadow, BMP280_CONFIG_REG, 0x10);    // Standby 0.5ms, Filter coeff 16

    // Первинна ініціалізація
    uint8_t id = 0;
    if (bmp280_raw_i2c_read(drv->escalation.i2c_hw.i2c, drv->i2c_addr, BMP280_CHIP_ID_REG, &id) != 0 || id != BMP280_EXPECTED_ID) {
        return bmp280_recover_and_restore(drv);
    }

    // Запис конфігурації
    for (uint8_t i = 0; i < drv->shadow.reg_count; i++) {
        bmp280_raw_i2c_write(drv->escalation.i2c_hw.i2c, drv->i2c_addr,
                             drv->shadow.registers[i].reg_addr,
                             drv->shadow.registers[i].value);
    }

    return 0;
}

int bmp280_read_temperature_pressure(bmp280_resilient_driver_t *drv, int32_t *temp, uint32_t *press) {
    uint8_t data[6];
    for (uint8_t i = 0; i < 6; i++) {
        int res = bmp280_raw_i2c_read(drv->escalation.i2c_hw.i2c, drv->i2c_addr, (uint8_t)(0xF7 + i), &data[i]);
        if (res != 0) {
            // Апаратна аварія під час читання: запускаємо відновлення
            bmp280_recover_and_restore(drv);
            return -1;
        }
    }

    *press = (uint32_t)((data[0] << 12) | (data[1] << 4) | (data[2] >> 4));
    *temp = (int32_t)((data[3] << 12) | (data[4] << 4) | (data[5] >> 4));
    return 0;
}
