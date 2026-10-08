#include "ina226.h"
#include <math.h>
#include <string.h>

/**
 * @file ina226.c
 * @brief Реалізація процедур низькорівневого C-драйвера монітора живлення INA226.
 */

/* Внутрішній коефіцієнт шкалювання для обчислення CAL (згідно з даташитом INA226) */
#define INA226_CAL_SCALING_FIXED_FACTOR  0.00512f

/* Кроки дискретизації АЦП за замовчуванням */
#define INA226_SHUNT_VOLTAGE_LSB_VOLTS   0.0000025f  /* 2.5 мкВ / LSB */
#define INA226_BUS_VOLTAGE_LSB_VOLTS     0.00125f    /* 1.25 мВ / LSB */

ina226_err_t ina226_write_reg_16(ina226_handle_t *handle, uint8_t reg_addr, uint16_t value)
{
    if (handle == NULL || handle->config.i2c_write == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    /* INA226 приймає дані у форматі Big-Endian (спочатку старший байт MSB, потім LSB) */
    uint8_t buffer[2];
    buffer[0] = (uint8_t)((value >> 8) & 0xFF);
    buffer[1] = (uint8_t)(value & 0xFF);

    return handle->config.i2c_write(handle->config.i2c_addr, reg_addr, buffer, 2);
}

ina226_err_t ina226_read_reg_16(ina226_handle_t *handle, uint8_t reg_addr, uint16_t *value)
{
    if (handle == NULL || value == NULL || handle->config.i2c_read == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    uint8_t buffer[2] = {0};
    ina226_err_t status = handle->config.i2c_read(handle->config.i2c_addr, reg_addr, buffer, 2);
    if (status != INA226_OK) {
        return status;
    }

    /* Конвертація з Big-Endian (MSB + LSB) у локальний формат uint16_t */
    *value = (uint16_t)(((uint16_t)buffer[0] << 8) | buffer[1]);
    return INA226_OK;
}

ina226_err_t ina226_soft_reset(ina226_handle_t *handle)
{
    if (handle == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    /* Запис 1 у старший біт (RST) конфігураційного регістра */
    ina226_err_t status = ina226_write_reg_16(handle, INA226_REG_CONFIG, INA226_CONFIG_RESET);
    if (status != INA226_OK) {
        return status;
    }

    return INA226_OK;
}

ina226_err_t ina226_calibrate(ina226_handle_t *handle, float r_shunt_ohms, float max_expected_current_a)
{
    if (handle == NULL || r_shunt_ohms <= 0.0f || max_expected_current_a <= 0.0f) {
        return INA226_ERR_INVALID_PARAM;
    }

    /* 
     * Крок 1: Розрахунок Current_LSB
     * За формулою: Current_LSB = Max_Expected_Current / 32768
     */
    float current_lsb = max_expected_current_a / 32768.0f;

    /*
     * Крок 2: Обчислення регістра калібрування CAL
     * Формула даташиту: CAL = trunc(0.00512 / (Current_LSB * R_shunt))
     */
    float cal_float = INA226_CAL_SCALING_FIXED_FACTOR / (current_lsb * r_shunt_ohms);

    if (cal_float < 1.0f || cal_float > 65535.0f) {
        return INA226_ERR_CALIBRATION;
    }

    uint16_t cal_value = (uint16_t)floorf(cal_float);

    /*
     * Крок 3: Переуточнення фактичного Current_LSB на основі цілочисельного CAL
     * Current_LSB_actual = 0.00512 / (CAL * R_shunt)
     */
    float actual_current_lsb = INA226_CAL_SCALING_FIXED_FACTOR / ((float)cal_value * r_shunt_ohms);

    /*
     * Крок 4: Розрахунок Power_LSB
     * Формула даташиту: Power_LSB = 25 * Current_LSB
     */
    float power_lsb = 25.0f * actual_current_lsb;

    /* Запис значень у контекст драйвера */
    handle->current_lsb_a = actual_current_lsb;
    handle->power_lsb_w = power_lsb;
    handle->cal_value = cal_value;
    handle->config.r_shunt_ohms = r_shunt_ohms;
    handle->config.max_expected_current_a = max_expected_current_a;

    /* Запис калібрувального значення у 16-бітний регістр CALIBRATION (0x05) */
    return ina226_write_reg_16(handle, INA226_REG_CALIBRATION, cal_value);
}

ina226_err_t ina226_init(ina226_handle_t *handle, const ina226_config_t *config)
{
    if (handle == NULL || config == NULL || config->i2c_write == NULL || config->i2c_read == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    memset(handle, 0, sizeof(ina226_handle_t));
    handle->config = *config;

    /* Перевірка наявності пристрою за допомогою зчитування ID виробника (0xFE) */
    uint16_t mfg_id = 0;
    ina226_err_t status = ina226_read_reg_16(handle, INA226_REG_MANUFACTURER_ID, &mfg_id);
    if (status != INA226_OK || mfg_id != INA226_MANUFACTURER_ID_VAL) {
        return INA226_ERR_DEV_NOT_FOUND;
    }

    /* Перевірка ідентифікатора кристала INA226 (0xFF) */
    uint16_t die_id = 0;
    status = ina226_read_reg_16(handle, INA226_REG_DIE_ID, &die_id);
    if (status != INA226_OK || (die_id & 0xFFF0) != INA226_DIE_ID_VAL) {
        return INA226_ERR_DEV_NOT_FOUND;
    }

    /* Програмне скидання пристрою перед формуванням налаштувань */
    status = ina226_soft_reset(handle);
    if (status != INA226_OK) {
        return status;
    }

    /* Формування бітового значення конфігураційного регістра (CONFIG 0x00) */
    uint16_t config_reg = ((uint16_t)(config->avg_mode & 0x07) << 9) |
                         ((uint16_t)(config->vbus_ct & 0x07)  << 6) |
                         ((uint16_t)(config->vsh_ct & 0x07)   << 3) |
                         ((uint16_t)(config->mode & 0x07));

    status = ina226_write_reg_16(handle, INA226_REG_CONFIG, config_reg);
    if (status != INA226_OK) {
        return status;
    }

    /* Виконання калібрування струмового каналу */
    status = ina226_calibrate(handle, config->r_shunt_ohms, config->max_expected_current_a);
    if (status != INA226_OK) {
        return status;
    }

    handle->is_initialized = true;
    return INA226_OK;
}

ina226_err_t ina226_read_shunt_voltage(ina226_handle_t *handle, float *shunt_v)
{
    if (handle == NULL || !handle->is_initialized || shunt_v == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    uint16_t raw_u16 = 0;
    ina226_err_t status = ina226_read_reg_16(handle, INA226_REG_SHUNT_VOLTAGE, &raw_u16);
    if (status != INA226_OK) {
        return status;
    }

    /* Напруга шунта — це 16-бітне знакове число у доповняльному коді (2's complement) */
    int16_t raw_s16 = (int16_t)raw_u16;
    *shunt_v = (float)raw_s16 * INA226_SHUNT_VOLTAGE_LSB_VOLTS;
    return INA226_OK;
}

ina226_err_t ina226_read_bus_voltage(ina226_handle_t *handle, float *bus_v)
{
    if (handle == NULL || !handle->is_initialized || bus_v == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    uint16_t raw_u16 = 0;
    ina226_err_t status = ina226_read_reg_16(handle, INA226_REG_BUS_VOLTAGE, &raw_u16);
    if (status != INA226_OK) {
        return status;
    }

    /* Напруга шини — це 16-бітне беззнакове число, 1 LSB = 1.25 мВ */
    *bus_v = (float)raw_u16 * INA226_BUS_VOLTAGE_LSB_VOLTS;
    return INA226_OK;
}

ina226_err_t ina226_read_current(ina226_handle_t *handle, float *current_a)
{
    if (handle == NULL || !handle->is_initialized || current_a == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    uint16_t raw_u16 = 0;
    ina226_err_t status = ina226_read_reg_16(handle, INA226_REG_CURRENT, &raw_u16);
    if (status != INA226_OK) {
        return status;
    }

    /* Струм — це 16-бітне знакове число у доповняльному коді (2's complement) */
    int16_t raw_s16 = (int16_t)raw_u16;
    *current_a = (float)raw_s16 * handle->current_lsb_a;
    return INA226_OK;
}

ina226_err_t ina226_read_power(ina226_handle_t *handle, float *power_w)
{
    if (handle == NULL || !handle->is_initialized || power_w == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    uint16_t raw_u16 = 0;
    ina226_err_t status = ina226_read_reg_16(handle, INA226_REG_POWER, &raw_u16);
    if (status != INA226_OK) {
        return status;
    }

    /* Потужність — це 16-бітне беззнакове значення */
    *power_w = (float)raw_u16 * handle->power_lsb_w;
    return INA226_OK;
}

ina226_err_t ina226_read_data(ina226_handle_t *handle, ina226_data_t *data)
{
    if (handle == NULL || !handle->is_initialized || data == NULL) {
        return INA226_ERR_INVALID_PARAM;
    }

    uint16_t raw_shunt = 0;
    uint16_t raw_bus = 0;
    uint16_t raw_curr = 0;
    uint16_t raw_pow = 0;

    ina226_err_t status = ina226_read_reg_16(handle, INA226_REG_SHUNT_VOLTAGE, &raw_shunt);
    if (status != INA226_OK) return status;

    status = ina226_read_reg_16(handle, INA226_REG_BUS_VOLTAGE, &raw_bus);
    if (status != INA226_OK) return status;

    status = ina226_read_reg_16(handle, INA226_REG_CURRENT, &raw_curr);
    if (status != INA226_OK) return status;

    status = ina226_read_reg_16(handle, INA226_REG_POWER, &raw_pow);
    if (status != INA226_OK) return status;

    /* Перетворення значень у знакові 16-бітні та фізичні величини */
    data->raw_shunt_reg = (int16_t)raw_shunt;
    data->raw_bus_reg = raw_bus;
    data->raw_current_reg = (int16_t)raw_curr;
    data->raw_power_reg = raw_pow;

    data->shunt_voltage_v = (float)data->raw_shunt_reg * INA226_SHUNT_VOLTAGE_LSB_VOLTS;
    data->bus_voltage_v = (float)data->raw_bus_reg * INA226_BUS_VOLTAGE_LSB_VOLTS;
    data->current_a = (float)data->raw_current_reg * handle->current_lsb_a;
    data->power_w = (float)data->raw_power_reg * handle->power_lsb_w;

    return INA226_OK;
}
