#include "../include/ina219.h"
#include <math.h>

/**
 * @file ina219.c
 * @brief Реалізація процедур bare-metal C-драйвера INA219.
 */

/* Допоміжні локальні функції для роботи з 16-бітними реєстрами INA219 */

static i2c_status_t ina219_write_register(ina219_t *dev, uint8_t reg, uint16_t value) {
    if (!dev || !dev->i2c) {
        return I2C_ERR_PARAM;
    }
    return i2c_write_reg16(dev->i2c, dev->config.i2c_addr, reg, value);
}

static i2c_status_t ina219_read_register(ina219_t *dev, uint8_t reg, uint16_t *value) {
    if (!dev || !dev->i2c || !value) {
        return I2C_ERR_PARAM;
    }
    return i2c_read_reg16(dev->i2c, dev->config.i2c_addr, reg, value);
}

/**
 * @brief Обчислює значення регістру Calibration на основі опору шунта та максимального струму.
 *
 * Формула Texas Instruments для INA219:
 * 1. Current_LSB = Max_Expected_Current / 32768.0
 * 2. Cal = trunc(0.04096 / (Current_LSB * Rshunt))
 * 3. Power_LSB = 20 * Current_LSB
 *
 * Біт 0 регістру Calibration завжди дорівнює 0 (void bit).
 */
uint16_t ina219_calculate_calibration(float r_shunt_ohms, float max_expected_i, float *out_current_lsb) {
    if (r_shunt_ohms <= 0.0f || max_expected_i <= 0.0f) {
        if (out_current_lsb) {
            *out_current_lsb = 0.0f;
        }
        return 0;
    }

    /* Розрахунок дискретності струму (Current LSB) */
    float current_lsb = max_expected_i / 32768.0f;

    if (out_current_lsb) {
        *out_current_lsb = current_lsb;
    }

    /* Розрахунок 16-бітного калібрувального значення */
    float cal_float = 0.04096f / (current_lsb * r_shunt_ohms);
    uint16_t cal_val = (uint16_t)floorf(cal_float);

    /* Очищаємо молодший біт FS0, який у чипі INA219 зафіксований у 0 */
    cal_val &= 0xFFFEU;

    return cal_val;
}

/**
 * @brief Записує обчислене значення калібрування в регістр Calibration.
 */
i2c_status_t ina219_write_calibration(ina219_t *dev) {
    if (!dev) {
        return I2C_ERR_PARAM;
    }
    return ina219_write_register(dev, INA219_REG_CALIBRATION, dev->cal_value);
}

/**
 * @brief Виконує програмний скид пристрою INA219 (Software Reset).
 */
i2c_status_t ina219_reset(ina219_t *dev) {
    if (!dev) {
        return I2C_ERR_PARAM;
    }
    i2c_status_t status = ina219_write_register(dev, INA219_REG_CONFIG, INA219_CONFIG_RESET);
    if (status != I2C_OK) {
        return status;
    }

    /* Очікуємо завершення скиду (чип очищає біт RST у 0) */
    uint16_t config_reg = 0;
    for (uint32_t i = 0; i < 1000; i++) {
        status = ina219_read_register(dev, INA219_REG_CONFIG, &config_reg);
        if (status == I2C_OK && !(config_reg & INA219_CONFIG_RESET)) {
            break;
        }
    }
    return status;
}

/**
 * @brief Ініціалізує драйвер INA219, програмує калібрування та конфігураційний регістр.
 */
i2c_status_t ina219_init(ina219_t *dev, i2c_bus_t *i2c, const ina219_config_t *cfg) {
    if (!dev || !i2c || !cfg) {
        return I2C_ERR_PARAM;
    }

    dev->i2c = i2c;
    dev->config = *cfg;

    /* Виконуємо розрахунок калібрувального коефіцієнта */
    dev->cal_value = ina219_calculate_calibration(cfg->r_shunt_ohms,
                                                  cfg->max_expected_i,
                                                  &dev->current_lsb_a);
    dev->power_lsb_w = 20.0f * dev->current_lsb_a;

    /* Скидання пристрою до початкового стану */
    i2c_status_t status = ina219_reset(dev);
    if (status != I2C_OK) {
        return status;
    }

    /* Запис регістру калібрування */
    status = ina219_write_calibration(dev);
    if (status != I2C_OK) {
        return status;
    }

    /* Формування значення Configuration Register (0x00) */
    uint16_t config_val = (uint16_t)((cfg->bus_range << 13) |
                                     (cfg->pga_gain << 11) |
                                     (cfg->bus_adc << 7) |
                                     (cfg->shunt_adc << 3) |
                                     (cfg->mode));

    return ina219_write_register(dev, INA219_REG_CONFIG, config_val);
}

/**
 * @brief Зчитує напругу шини та аналізує апаратні прапорці CNVR і OVF.
 */
i2c_status_t ina219_read_bus_voltage(ina219_t *dev, float *voltage_v, bool *cnvr, bool *ovf) {
    uint16_t raw_reg = 0;
    i2c_status_t status = ina219_read_register(dev, INA219_REG_BUS_VOLTAGE, &raw_reg);
    if (status != I2C_OK) {
        return status;
    }

    /* Перевірка статусних бітів: біт 1 - CNVR, біт 0 - OVF */
    if (cnvr) {
        *cnvr = (raw_reg & INA219_BUS_VOLTAGE_CNVR) != 0;
    }
    if (ovf) {
        *ovf = (raw_reg & INA219_BUS_VOLTAGE_OVF) != 0;
    }

    /* Значення напруги шини знаходиться в бітах [15:3]. 1 LSB = 4 мВ = 0.004 В */
    uint16_t raw_val = (raw_reg >> INA219_BUS_VOLTAGE_RAW_SHIFT);
    if (voltage_v) {
        *voltage_v = (float)raw_val * 0.004f;
    }

    return I2C_OK;
}

/**
 * @brief Зчитує падіння напруги на шунті в мілівольтах.
 */
i2c_status_t ina219_read_shunt_voltage(ina219_t *dev, float *shunt_mv) {
    uint16_t raw_reg = 0;
    i2c_status_t status = ina219_read_register(dev, INA219_REG_SHUNT_VOLTAGE, &raw_reg);
    if (status != I2C_OK) {
        return status;
    }

    /* Регістр Shunt Voltage є знаковим 16-бітним числом у коді з доповненням до двох (2's complement).
     * Дискретність 1 LSB = 10 мкВ = 0.01 мВ */
    int16_t raw_signed = (int16_t)raw_reg;
    if (shunt_mv) {
        *shunt_mv = (float)raw_signed * 0.01f;
    }

    return I2C_OK;
}

/**
 * @brief Зчитує виміряний струм у міліамперах.
 */
i2c_status_t ina219_read_current(ina219_t *dev, float *current_ma) {
    uint16_t raw_reg = 0;
    i2c_status_t status = ina219_read_register(dev, INA219_REG_CURRENT, &raw_reg);
    if (status != I2C_OK) {
        return status;
    }

    /* Струм повертається як знакове 16-бітне число. Струм = Current_Reg * Current_LSB */
    int16_t raw_signed = (int16_t)raw_reg;
    if (current_ma) {
        *current_ma = ((float)raw_signed * dev->current_lsb_a) * 1000.0f;
    }

    return I2C_OK;
}

/**
 * @brief Зчитує обчислену чипом потужність у міліватах.
 */
i2c_status_t ina219_read_power(ina219_t *dev, float *power_mw) {
    uint16_t raw_reg = 0;
    i2c_status_t status = ina219_read_register(dev, INA219_REG_POWER, &raw_reg);
    if (status != I2C_OK) {
        return status;
    }

    /* Потужність є беззнаковим 16-бітним числом. Потужність = Power_Reg * Power_LSB */
    if (power_mw) {
        *power_mw = ((float)raw_reg * dev->power_lsb_w) * 1000.0f;
    }

    return I2C_OK;
}

/**
 * @brief Зчитує повний кадр телеметрії з перевіркою прапорців CNVR та OVF.
 */
i2c_status_t ina219_read_telemetry(ina219_t *dev, ina219_data_t *data) {
    if (!dev || !data) {
        return I2C_ERR_PARAM;
    }

    /* Спочатку читаємо Bus Voltage, щоб перевірити CNVR і OVF */
    i2c_status_t status = ina219_read_bus_voltage(dev, &data->voltage_v, &data->conversion_ready, &data->math_overflow);
    if (status != I2C_OK) {
        return status;
    }

    /* Зчитуємо спад напруги на шунті */
    status = ina219_read_shunt_voltage(dev, &data->shunt_voltage_mv);
    if (status != I2C_OK) {
        return status;
    }

    /* Зчитуємо струм */
    status = ina219_read_current(dev, &data->current_ma);
    if (status != I2C_OK) {
        return status;
    }

    /* Зчитуємо потужність */
    status = ina219_read_power(dev, &data->power_mw);
    if (status != I2C_OK) {
        return status;
    }

    return I2C_OK;
}
