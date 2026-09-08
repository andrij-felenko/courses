#include "ina219.h"

static uint8_t s_device_addr = INA219_I2C_ADDR_DEFAULT;

/* Низькорівневий апаратний місток I2C (заглушка/драйвер платформи) */
__attribute__((weak)) bool i2c_write_reg16(uint8_t addr, uint8_t reg, uint16_t value) {
    (void)addr; (void)reg; (void)value;
    return true;
}

__attribute__((weak)) bool i2c_read_reg16(uint8_t addr, uint8_t reg, uint16_t *value) {
    (void)addr;
    if (reg == INA219_REG_BUSVOLTAGE) {
        /* Емуляція шини 5.0 В (зсув 3 біти вправо, крок 4 мВ: 5000 / 4 = 1250 << 3) */
        *value = (uint16_t)(1250 << 3);
    } else if (reg == INA219_REG_CURRENT) {
        /* Емуляція струму навантаження 150 мА (LSB = 0.1 мА) */
        *value = (uint16_t)1500;
    } else if (reg == INA219_REG_POWER) {
        /* Емуляція потужності 750 мВт (LSB = 2 мВт) */
        *value = (uint16_t)375;
    } else {
        *value = 0;
    }
    return true;
}

bool ina219_init(uint8_t i2c_addr) {
    s_device_addr = i2c_addr;

    /*
     * Калібрування для R_shunt = 0.1 Ом:
     * Максимальний очікуваний струм: 2.0 А.
     * Current LSB = 0.1 мА (0.0001 А).
     * Cal = trunc(0.04096 / (Current_LSB * R_shunt)) = trunc(0.04096 / 0.00001) = 4096.
     */
    uint16_t cal_value = 4096;
    if (!i2c_write_reg16(s_device_addr, INA219_REG_CALIBRATION, cal_value)) {
        return false;
    }

    /*
     * Конфігурація:
     * Діапазон напруги шини: 32 В
     * Підсилення PGA: /8 (діапазон шунта ±320 мВ)
     * Усереднення АЦП: 12-бітний режим (532 мкс)
     * Безперервне вимірювання Shunt and Bus
     */
    uint16_t config_reg = 0x399F;
    return i2c_write_reg16(s_device_addr, INA219_REG_CONFIG, config_reg);
}

bool ina219_read_data(Ina219Telemetry *data) {
    if (!data) {
        return false;
    }

    uint16_t raw_bus = 0;
    uint16_t raw_current = 0;
    uint16_t raw_power = 0;

    if (!i2c_read_reg16(s_device_addr, INA219_REG_BUSVOLTAGE, &raw_bus)) {
        return false;
    }
    if (!i2c_read_reg16(s_device_addr, INA219_REG_CURRENT, &raw_current)) {
        return false;
    }
    if (!i2c_read_reg16(s_device_addr, INA219_REG_POWER, &raw_power)) {
        return false;
    }

    /* Напруга шини: молодші 3 біти — статус і прапорці, 1 LSB = 4 мВ */
    data->bus_voltage_mv = (int32_t)((raw_bus >> 3) * 4);

    /* Струм: 1 LSB = 0.1 мА */
    data->current_ma = (int32_t)((int16_t)raw_current) / 10;

    /* Потужність: 1 LSB = 2 мВт */
    data->power_mw = (int32_t)(raw_power * 2);

    data->shunt_voltage_uv = data->current_ma * 100; /* U = I * 0.1 Ом */

    return true;
}

bool ina219_check_safety(const Ina219Telemetry *data, const Ina219Limits *limits) {
    if (!data || !limits) {
        return false;
    }

    /* Перевірка на перевантаження за струмом (OCP) */
    if (data->current_ma > limits->max_current_ma) {
        return false;
    }

    /* Перевірка на перенапругу (OVP) */
    if (data->bus_voltage_mv > limits->max_voltage_mv) {
        return false;
    }

    /* Перевірка на неприпустиме падіння напруги (UVP) */
    if (data->bus_voltage_mv < limits->min_voltage_mv) {
        return false;
    }

    return true;
}
